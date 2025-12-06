"""
Smart Classroom Database Service - Secure Access Control System
Implements secure data storage with audit logging and RBAC
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import hashlib
import secrets

# Import security service for password hashing
try:
    from core.security import security_service
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

from config import config


class Database:
    """
    SQLite database service with security features:
    - Secure password hashing (bcrypt)
    - Audit logging
    - Login attempt tracking
    - Password history
    - Role-based access control
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.conn = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._create_security_tables()
        self._create_default_admin()
    
    def _create_tables(self):
        """Create all required tables"""
        cursor = self.conn.cursor()
        
        # Users table with security fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                profile_image TEXT,
                is_active INTEGER DEFAULT 1,
                failed_login_attempts INTEGER DEFAULT 0,
                last_failed_login TIMESTAMP,
                last_login TIMESTAMP,
                password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Classes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                instructor_id INTEGER NOT NULL,
                schedule TEXT,
                room TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instructor_id) REFERENCES users(id)
            )
        ''')
        
        # Class enrollments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id),
                FOREIGN KEY (student_id) REFERENCES users(id),
                UNIQUE(class_id, student_id)
            )
        ''')
        
        # Attendance sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                session_date DATE NOT NULL,
                qr_code TEXT UNIQUE,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id)
            )
        ''')
        
        # Attendance records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                status TEXT DEFAULT 'present',
                marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (session_id) REFERENCES attendance_sessions(id),
                FOREIGN KEY (student_id) REFERENCES users(id),
                UNIQUE(session_id, student_id)
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, key)
            )
        ''')
        
        # Sync queue for offline operations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        # Classrooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classrooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                building TEXT DEFAULT 'CICS Building',
                floor TEXT,
                capacity INTEGER DEFAULT 40,
                status TEXT DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Room schedules/bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                instructor_id INTEGER NOT NULL,
                subject_name TEXT NOT NULL,
                schedule_date DATE NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT DEFAULT 'scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES classrooms(id),
                FOREIGN KEY (instructor_id) REFERENCES users(id)
            )
        ''')
        
        self.conn.commit()
        
        # Initialize default classrooms if empty
        self._init_classrooms()
    
    def _create_security_tables(self):
        """Create security-related tables"""
        cursor = self.conn.cursor()
        
        # Audit logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                category TEXT,
                user_id INTEGER,
                username TEXT,
                success INTEGER DEFAULT 1,
                ip_address TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Password history table (for reuse prevention)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Sessions table for tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # User activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                description TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        self.conn.commit()
    
    def _create_default_admin(self):
        """Create default admin user if none exists"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
        if cursor.fetchone()['count'] == 0:
            # Create default admin
            admin_password = "Admin@123"  # Should be changed on first login
            self.create_user(
                student_id="ADMIN001",
                email="admin@smartclassroom.edu",
                password=admin_password,
                first_name="System",
                last_name="Administrator",
                role="admin"
            )
            print("[DATABASE] Default admin created: ADMIN001 / Admin@123")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt (via security service) or SHA-256 fallback"""
        if SECURITY_AVAILABLE:
            return security_service.hash_password(password)
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if SECURITY_AVAILABLE:
            return security_service.verify_password(password, hashed)
        # Fallback for legacy hashes
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, student_id: str, email: str, password: str, 
                    first_name: str, last_name: str, role: str = "student") -> Optional[int]:
        """Create a new user with secure password hashing"""
        try:
            cursor = self.conn.cursor()
            password_hash = self._hash_password(password)
            cursor.execute('''
                INSERT INTO users (student_id, email, password_hash, first_name, last_name, role, password_changed_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (student_id, email, password_hash, first_name, last_name, role))
            self.conn.commit()
            user_id = cursor.lastrowid
            
            # Store initial password in history
            self._add_password_history(user_id, password_hash)
            
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    def authenticate_user(self, student_id: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with security controls:
        - Account lockout check
        - Password verification
        - Login attempt tracking
        - Last login update
        """
        cursor = self.conn.cursor()
        
        # Get user by student_id
        cursor.execute('SELECT * FROM users WHERE student_id = ?', (student_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        user = dict(row)
        
        # Check if account is active
        if not user.get('is_active', 1):
            return None  # Account disabled
        
        # Check for account lockout
        failed_attempts = user.get('failed_login_attempts', 0)
        last_failed = user.get('last_failed_login')
        
        if failed_attempts >= config.MAX_LOGIN_ATTEMPTS and last_failed:
            try:
                last_failed_dt = datetime.fromisoformat(last_failed)
                lockout_end = last_failed_dt + timedelta(minutes=config.LOCKOUT_DURATION_MINUTES)
                if datetime.now() < lockout_end:
                    return None  # Account still locked
                else:
                    # Lockout expired, reset attempts
                    self._reset_login_attempts(user['id'])
            except:
                pass
        
        # Verify password
        if self._verify_password(password, user['password_hash']):
            # Successful login
            self._reset_login_attempts(user['id'])
            self._update_last_login(user['id'])
            return user
        else:
            # Failed login
            self._increment_login_attempts(user['id'])
            return None
    
    def _increment_login_attempts(self, user_id: int):
        """Increment failed login attempts"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users SET 
                failed_login_attempts = failed_login_attempts + 1,
                last_failed_login = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (user_id,))
        self.conn.commit()
    
    def _reset_login_attempts(self, user_id: int):
        """Reset failed login attempts"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users SET failed_login_attempts = 0, last_failed_login = NULL WHERE id = ?
        ''', (user_id,))
        self.conn.commit()
    
    def _update_last_login(self, user_id: int):
        """Update last login timestamp"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
        self.conn.commit()
    
    def _add_password_history(self, user_id: int, password_hash: str):
        """Add password to history"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO password_history (user_id, password_hash) VALUES (?, ?)
        ''', (user_id, password_hash))
        
        # Keep only last N passwords
        cursor.execute('''
            DELETE FROM password_history WHERE user_id = ? AND id NOT IN (
                SELECT id FROM password_history WHERE user_id = ? 
                ORDER BY created_at DESC LIMIT ?
            )
        ''', (user_id, user_id, config.PASSWORD_HISTORY_COUNT))
        self.conn.commit()
    
    def check_password_reuse(self, user_id: int, new_password: str) -> bool:
        """Check if password was recently used (returns True if reused)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT password_hash FROM password_history WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
        ''', (user_id, config.PASSWORD_HISTORY_COUNT))
        
        for row in cursor.fetchall():
            if self._verify_password(new_password, row['password_hash']):
                return True
        return False
    
    def get_login_attempts(self, user_id: int) -> Dict:
        """Get login attempt info for a user"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT failed_login_attempts, last_failed_login FROM users WHERE id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else {'failed_login_attempts': 0, 'last_failed_login': None}
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user and all their related data"""
        try:
            cursor = self.conn.cursor()
            
            # Delete user's room schedules
            cursor.execute('DELETE FROM room_schedules WHERE instructor_id = ?', (user_id,))
            
            # Delete user's settings
            cursor.execute('DELETE FROM settings WHERE user_id = ?', (user_id,))
            
            # Delete user's attendance records
            cursor.execute('DELETE FROM attendance_records WHERE student_id = ?', (user_id,))
            
            # Delete user's enrollments
            cursor.execute('DELETE FROM enrollments WHERE student_id = ?', (user_id,))
            
            # Delete user's sync queue items
            cursor.execute('DELETE FROM sync_queue WHERE user_id = ?', (user_id,))
            
            # Finally, delete the user
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        if not kwargs:
            return False
        
        allowed_fields = ['email', 'first_name', 'last_name', 'profile_image']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        
        cursor = self.conn.cursor()
        cursor.execute(f'''
            UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_password(self, user_id: int, new_password: str, check_history: bool = True) -> tuple:
        """
        Update user password with security checks.
        Returns (success: bool, error_message: str or None)
        """
        # Check password reuse
        if check_history and self.check_password_reuse(user_id, new_password):
            return False, "Cannot reuse recent passwords"
        
        password_hash = self._hash_password(new_password)
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users SET 
                password_hash = ?, 
                password_changed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (password_hash, user_id))
        self.conn.commit()
        
        if cursor.rowcount > 0:
            # Add to password history
            self._add_password_history(user_id, password_hash)
            return True, None
        return False, "Failed to update password"
    
    # ==================== ADMIN USER MANAGEMENT ====================
    
    def get_all_users(self, include_inactive: bool = False) -> List[Dict]:
        """Get all users (admin function)"""
        cursor = self.conn.cursor()
        if include_inactive:
            cursor.execute('''
                SELECT id, student_id, email, first_name, last_name, role, 
                       is_active, last_login, created_at, failed_login_attempts
                FROM users ORDER BY created_at DESC
            ''')
        else:
            cursor.execute('''
                SELECT id, student_id, email, first_name, last_name, role,
                       is_active, last_login, created_at, failed_login_attempts
                FROM users WHERE is_active = 1 ORDER BY created_at DESC
            ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_user_by_student_id(self, student_id: str) -> Optional[Dict]:
        """Get user by student ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE student_id = ?', (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def disable_user(self, user_id: int) -> bool:
        """Disable a user account (soft delete)"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def enable_user(self, user_id: int) -> bool:
        """Enable a disabled user account"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_active = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def change_user_role(self, user_id: int, new_role: str) -> bool:
        """Change user role (admin function)"""
        valid_roles = ['student', 'instructor', 'admin']
        if new_role not in valid_roles:
            return False
        
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (new_role, user_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def unlock_user_account(self, user_id: int) -> bool:
        """Unlock a locked user account (reset failed attempts)"""
        return self._reset_login_attempts(user_id) or True
    
    def get_user_count_by_role(self) -> Dict[str, int]:
        """Get count of users by role"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT role, COUNT(*) as count FROM users 
            WHERE is_active = 1 GROUP BY role
        ''')
        return {row['role']: row['count'] for row in cursor.fetchall()}
    
    # ==================== AUDIT LOG OPERATIONS ====================
    
    def add_audit_log(self, action: str, category: str = None, user_id: int = None,
                      username: str = None, success: bool = True, 
                      ip_address: str = None, details: str = None) -> int:
        """Add an entry to the audit log"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO audit_logs (action, category, user_id, username, success, ip_address, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (action, category, user_id, username, 1 if success else 0, ip_address, details))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_audit_logs(self, limit: int = 100, offset: int = 0, 
                       action_filter: str = None, user_filter: int = None,
                       date_from: str = None, date_to: str = None) -> List[Dict]:
        """Get audit logs with optional filters"""
        cursor = self.conn.cursor()
        
        query = 'SELECT * FROM audit_logs WHERE 1=1'
        params = []
        
        if action_filter:
            query += ' AND action = ?'
            params.append(action_filter)
        
        if user_filter:
            query += ' AND user_id = ?'
            params.append(user_filter)
        
        if date_from:
            query += ' AND created_at >= ?'
            params.append(date_from)
        
        if date_to:
            query += ' AND created_at <= ?'
            params.append(date_to)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_audit_log_count(self, action_filter: str = None, user_filter: int = None) -> int:
        """Get total count of audit logs"""
        cursor = self.conn.cursor()
        
        query = 'SELECT COUNT(*) as count FROM audit_logs WHERE 1=1'
        params = []
        
        if action_filter:
            query += ' AND action = ?'
            params.append(action_filter)
        
        if user_filter:
            query += ' AND user_id = ?'
            params.append(user_filter)
        
        cursor.execute(query, params)
        return cursor.fetchone()['count']
    
    def get_audit_action_types(self) -> List[str]:
        """Get list of unique audit action types"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT action FROM audit_logs ORDER BY action')
        return [row['action'] for row in cursor.fetchall()]
    
    # ==================== USER ACTIVITY OPERATIONS ====================
    
    def log_user_activity(self, user_id: int, activity_type: str, 
                          description: str = None, ip_address: str = None) -> int:
        """Log user activity"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO user_activity (user_id, activity_type, description, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (user_id, activity_type, description, ip_address))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_activity(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get activity history for a user"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM user_activity WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
        ''', (user_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_logins(self, limit: int = 20) -> List[Dict]:
        """Get recent login activity"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.id, u.student_id, u.first_name, u.last_name, u.role, u.last_login
            FROM users u WHERE u.last_login IS NOT NULL
            ORDER BY u.last_login DESC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_failed_login_summary(self) -> List[Dict]:
        """Get summary of users with failed login attempts"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, student_id, first_name, last_name, 
                   failed_login_attempts, last_failed_login
            FROM users WHERE failed_login_attempts > 0
            ORDER BY failed_login_attempts DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== SESSION MANAGEMENT ====================
    
    def create_session(self, user_id: int, ip_address: str = None, 
                       user_agent: str = None) -> str:
        """Create a new session and return token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=config.SESSION_TIMEOUT_MINUTES)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, token, ip_address, user_agent, expires_at.isoformat()))
        self.conn.commit()
        return token
    
    def validate_session(self, token: str) -> Optional[Dict]:
        """Validate session token and return user if valid"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.*, u.* FROM user_sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ? AND s.is_active = 1
        ''', (token,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        session = dict(row)
        
        # Check expiration
        if session.get('expires_at'):
            try:
                expires = datetime.fromisoformat(session['expires_at'])
                if datetime.now() > expires:
                    self.invalidate_session(token)
                    return None
            except:
                pass
        
        return session
    
    def invalidate_session(self, token: str) -> bool:
        """Invalidate a session"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE session_token = ?', (token,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def invalidate_all_user_sessions(self, user_id: int) -> int:
        """Invalidate all sessions for a user"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE user_id = ?', (user_id,))
        self.conn.commit()
        return cursor.rowcount
    
    def get_active_sessions(self, user_id: int) -> List[Dict]:
        """Get all active sessions for a user"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM user_sessions 
            WHERE user_id = ? AND is_active = 1
            ORDER BY created_at DESC
        ''', (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== CLASS OPERATIONS ====================
    
    def create_class(self, class_code: str, name: str, instructor_id: int,
                     description: str = "", schedule: str = "", room: str = "") -> Optional[int]:
        """Create a new class"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO classes (class_code, name, description, instructor_id, schedule, room)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (class_code, name, description, instructor_id, schedule, room))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_class(self, class_id: int) -> Optional[Dict]:
        """Get class by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM classes WHERE id = ?', (class_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_classes_by_instructor(self, instructor_id: int) -> List[Dict]:
        """Get all classes by instructor"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.*, COUNT(e.id) as student_count
            FROM classes c
            LEFT JOIN enrollments e ON c.id = e.class_id
            WHERE c.instructor_id = ?
            GROUP BY c.id
            ORDER BY c.created_at DESC
        ''', (instructor_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_enrolled_classes(self, student_id: int) -> List[Dict]:
        """Get all classes a student is enrolled in"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.*, u.first_name || ' ' || u.last_name as instructor_name
            FROM classes c
            JOIN enrollments e ON c.id = e.class_id
            JOIN users u ON c.instructor_id = u.id
            WHERE e.student_id = ?
            ORDER BY c.name
        ''', (student_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_class(self, class_id: int, **kwargs) -> bool:
        """Update class information"""
        allowed_fields = ['name', 'description', 'schedule', 'room']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
        values = list(updates.values()) + [class_id]
        
        cursor = self.conn.cursor()
        cursor.execute(f'UPDATE classes SET {set_clause} WHERE id = ?', values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_class(self, class_id: int) -> bool:
        """Delete a class and related data"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM attendance_records WHERE session_id IN (SELECT id FROM attendance_sessions WHERE class_id = ?)', (class_id,))
        cursor.execute('DELETE FROM attendance_sessions WHERE class_id = ?', (class_id,))
        cursor.execute('DELETE FROM enrollments WHERE class_id = ?', (class_id,))
        cursor.execute('DELETE FROM classes WHERE id = ?', (class_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ==================== ENROLLMENT OPERATIONS ====================
    
    def enroll_student(self, class_id: int, student_id: int) -> bool:
        """Enroll a student in a class"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO enrollments (class_id, student_id) VALUES (?, ?)
            ''', (class_id, student_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def unenroll_student(self, class_id: int, student_id: int) -> bool:
        """Remove a student from a class"""
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM enrollments WHERE class_id = ? AND student_id = ?
        ''', (class_id, student_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_class_students(self, class_id: int) -> List[Dict]:
        """Get all students in a class"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.id, u.student_id, u.email, u.first_name, u.last_name, u.profile_image,
                   e.enrolled_at
            FROM users u
            JOIN enrollments e ON u.id = e.student_id
            WHERE e.class_id = ?
            ORDER BY u.last_name, u.first_name
        ''', (class_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== ATTENDANCE OPERATIONS ====================
    
    def create_attendance_session(self, class_id: int, session_date: str,
                                   qr_code: str = None, expires_minutes: int = 30) -> Optional[int]:
        """Create a new attendance session"""
        import uuid
        if not qr_code:
            qr_code = str(uuid.uuid4())
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO attendance_sessions (class_id, session_date, qr_code, expires_at)
                VALUES (?, ?, ?, datetime('now', '+' || ? || ' minutes'))
            ''', (class_id, session_date, qr_code, expires_minutes))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_attendance_session(self, session_id: int) -> Optional[Dict]:
        """Get attendance session by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM attendance_sessions WHERE id = ?', (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_session_by_qr(self, qr_code: str) -> Optional[Dict]:
        """Get attendance session by QR code"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM attendance_sessions 
            WHERE qr_code = ? AND status = 'active'
        ''', (qr_code,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_class_sessions(self, class_id: int) -> List[Dict]:
        """Get all attendance sessions for a class"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.*, 
                   COUNT(r.id) as present_count,
                   (SELECT COUNT(*) FROM enrollments WHERE class_id = ?) as total_students
            FROM attendance_sessions s
            LEFT JOIN attendance_records r ON s.id = r.session_id AND r.status = 'present'
            WHERE s.class_id = ?
            GROUP BY s.id
            ORDER BY s.session_date DESC
        ''', (class_id, class_id))
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_attendance(self, session_id: int, student_id: int, 
                        status: str = "present", notes: str = "") -> bool:
        """Mark student attendance"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO attendance_records (session_id, student_id, status, notes, marked_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (session_id, student_id, status, notes))
            self.conn.commit()
            return True
        except:
            return False
    
    def get_session_attendance(self, session_id: int) -> List[Dict]:
        """Get all attendance records for a session"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.id, u.student_id, u.first_name, u.last_name, u.profile_image,
                   COALESCE(r.status, 'absent') as status, r.marked_at, r.notes
            FROM enrollments e
            JOIN users u ON e.student_id = u.id
            LEFT JOIN attendance_records r ON r.session_id = ? AND r.student_id = u.id
            WHERE e.class_id = (SELECT class_id FROM attendance_sessions WHERE id = ?)
            ORDER BY u.last_name, u.first_name
        ''', (session_id, session_id))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_student_attendance_history(self, student_id: int, class_id: int = None) -> List[Dict]:
        """Get attendance history for a student"""
        cursor = self.conn.cursor()
        if class_id:
            cursor.execute('''
                SELECT s.session_date, c.name as class_name, c.class_code,
                       COALESCE(r.status, 'absent') as status
                FROM attendance_sessions s
                JOIN classes c ON s.class_id = c.id
                JOIN enrollments e ON e.class_id = c.id AND e.student_id = ?
                LEFT JOIN attendance_records r ON r.session_id = s.id AND r.student_id = ?
                WHERE c.id = ?
                ORDER BY s.session_date DESC
            ''', (student_id, student_id, class_id))
        else:
            cursor.execute('''
                SELECT s.session_date, c.name as class_name, c.class_code,
                       COALESCE(r.status, 'absent') as status
                FROM attendance_sessions s
                JOIN classes c ON s.class_id = c.id
                JOIN enrollments e ON e.class_id = c.id AND e.student_id = ?
                LEFT JOIN attendance_records r ON r.session_id = s.id AND r.student_id = ?
                ORDER BY s.session_date DESC
            ''', (student_id, student_id))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def get_class_analytics(self, class_id: int) -> Dict:
        """Get attendance analytics for a class"""
        cursor = self.conn.cursor()
        
        # Total sessions
        cursor.execute('SELECT COUNT(*) as count FROM attendance_sessions WHERE class_id = ?', (class_id,))
        total_sessions = cursor.fetchone()['count']
        
        # Total enrolled students
        cursor.execute('SELECT COUNT(*) as count FROM enrollments WHERE class_id = ?', (class_id,))
        total_students = cursor.fetchone()['count']
        
        # Attendance by session
        cursor.execute('''
            SELECT s.session_date, 
                   COUNT(CASE WHEN r.status = 'present' THEN 1 END) as present,
                   COUNT(CASE WHEN r.status = 'late' THEN 1 END) as late,
                   ? - COUNT(r.id) as absent
            FROM attendance_sessions s
            LEFT JOIN attendance_records r ON s.id = r.session_id
            WHERE s.class_id = ?
            GROUP BY s.id
            ORDER BY s.session_date
        ''', (total_students, class_id))
        sessions_data = [dict(row) for row in cursor.fetchall()]
        
        # Student attendance rates
        cursor.execute('''
            SELECT u.id, u.student_id, u.first_name, u.last_name,
                   COUNT(CASE WHEN r.status = 'present' THEN 1 END) as present_count,
                   COUNT(CASE WHEN r.status = 'late' THEN 1 END) as late_count,
                   ? as total_sessions
            FROM enrollments e
            JOIN users u ON e.student_id = u.id
            LEFT JOIN attendance_sessions s ON s.class_id = e.class_id
            LEFT JOIN attendance_records r ON r.session_id = s.id AND r.student_id = u.id
            WHERE e.class_id = ?
            GROUP BY u.id
            ORDER BY present_count DESC
        ''', (total_sessions, class_id))
        students_data = [dict(row) for row in cursor.fetchall()]
        
        # Calculate overall stats
        total_possible = total_sessions * total_students
        cursor.execute('''
            SELECT COUNT(*) as count FROM attendance_records r
            JOIN attendance_sessions s ON r.session_id = s.id
            WHERE s.class_id = ? AND r.status = 'present'
        ''', (class_id,))
        total_present = cursor.fetchone()['count']
        
        overall_rate = (total_present / total_possible * 100) if total_possible > 0 else 0
        
        return {
            'total_sessions': total_sessions,
            'total_students': total_students,
            'overall_attendance_rate': round(overall_rate, 1),
            'sessions_data': sessions_data,
            'students_data': students_data
        }
    
    def get_student_analytics(self, student_id: int) -> Dict:
        """Get attendance analytics for a student"""
        cursor = self.conn.cursor()
        
        # Classes enrolled
        cursor.execute('SELECT COUNT(*) as count FROM enrollments WHERE student_id = ?', (student_id,))
        total_classes = cursor.fetchone()['count']
        
        # Overall attendance
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN r.status = 'present' THEN 1 END) as present,
                COUNT(CASE WHEN r.status = 'late' THEN 1 END) as late,
                COUNT(s.id) as total
            FROM enrollments e
            JOIN attendance_sessions s ON s.class_id = e.class_id
            LEFT JOIN attendance_records r ON r.session_id = s.id AND r.student_id = ?
            WHERE e.student_id = ?
        ''', (student_id, student_id))
        attendance = cursor.fetchone()
        
        overall_rate = ((attendance['present'] + attendance['late']) / attendance['total'] * 100) if attendance['total'] > 0 else 0
        
        # Attendance by class
        cursor.execute('''
            SELECT c.id, c.name, c.class_code,
                   COUNT(s.id) as total_sessions,
                   COUNT(CASE WHEN r.status = 'present' THEN 1 END) as present,
                   COUNT(CASE WHEN r.status = 'late' THEN 1 END) as late
            FROM enrollments e
            JOIN classes c ON e.class_id = c.id
            LEFT JOIN attendance_sessions s ON s.class_id = c.id
            LEFT JOIN attendance_records r ON r.session_id = s.id AND r.student_id = ?
            WHERE e.student_id = ?
            GROUP BY c.id
        ''', (student_id, student_id))
        classes_data = [dict(row) for row in cursor.fetchall()]
        
        return {
            'total_classes': total_classes,
            'present_count': attendance['present'],
            'late_count': attendance['late'],
            'total_sessions': attendance['total'],
            'overall_attendance_rate': round(overall_rate, 1),
            'classes_data': classes_data
        }
    
    # ==================== SETTINGS OPERATIONS ====================
    
    def set_setting(self, user_id: int, key: str, value: str) -> bool:
        """Set a user setting"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (user_id, key, value) VALUES (?, ?, ?)
            ''', (user_id, key, value))
            self.conn.commit()
            return True
        except:
            return False
    
    def get_setting(self, user_id: int, key: str, default: str = None) -> Optional[str]:
        """Get a user setting"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE user_id = ? AND key = ?', (user_id, key))
        row = cursor.fetchone()
        return row['value'] if row else default
    
    def get_all_settings(self, user_id: int) -> Dict[str, str]:
        """Get all settings for a user"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT key, value FROM settings WHERE user_id = ?', (user_id,))
        return {row['key']: row['value'] for row in cursor.fetchall()}
    
    # ==================== SYNC OPERATIONS ====================
    
    def add_to_sync_queue(self, operation: str, table_name: str, 
                          record_id: int = None, data: Dict = None):
        """Add operation to sync queue for offline mode"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sync_queue (operation, table_name, record_id, data)
            VALUES (?, ?, ?, ?)
        ''', (operation, table_name, record_id, json.dumps(data) if data else None))
        self.conn.commit()
    
    def get_pending_sync(self) -> List[Dict]:
        """Get all pending sync operations"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM sync_queue WHERE synced = 0 ORDER BY created_at')
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_synced(self, sync_id: int):
        """Mark sync operation as completed"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE sync_queue SET synced = 1 WHERE id = ?', (sync_id,))
        self.conn.commit()
    
    # ==================== CLASSROOM OPERATIONS ====================
    
    def _init_classrooms(self):
        """Initialize default classrooms for CCS Building"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM classrooms')
        if cursor.fetchone()['count'] > 0:
            return
        
        # CCS Building Classrooms - Actual Layout
        classrooms = [
            # Ground Floor (1st) - Lecture Rooms
            ("Lecture Room 1", "LR-101", "CCS Building", "1st", 40),
            ("Lecture Room 2", "LR-102", "CCS Building", "1st", 40),
            ("Lecture Room 3", "LR-103", "CCS Building", "1st", 40),
            ("Lecture Room 4", "LR-104", "CCS Building", "1st", 40),
            ("Lecture Room 5", "LR-105", "CCS Building", "1st", 40),
            ("Lecture Room 6", "LR-106", "CCS Building", "1st", 40),
            
            # 2nd Floor - Faculty, Admin, Mac Lab, Open Lab
            ("Faculty Room", "FAC-201", "CCS Building", "2nd", 20),
            ("Dean's Office", "DEAN-202", "CCS Building", "2nd", 10),
            ("Repair Room", "REP-203", "CCS Building", "2nd", 15),
            ("Mac Lab", "MAC-204", "CCS Building", "2nd", 30),
            ("Open Lab", "OPEN-205", "CCS Building", "2nd", 50),
            
            # 3rd Floor - IT Labs, ERP Lab, CS Lab
            ("IT Lab 1", "IT-301", "CCS Building", "3rd", 40),
            ("IT Lab 2", "IT-302", "CCS Building", "3rd", 40),
            ("ERP Lab", "ERP-303", "CCS Building", "3rd", 35),
            ("CS Lab", "CS-304", "CCS Building", "3rd", 40),
            
            # 4th Floor - Rise Lab, Research, LIS Lab, NAS Lab
            ("Rise Lab", "RISE-401", "CCS Building", "4th", 35),
            ("Research Room", "RES-402", "CCS Building", "4th", 20),
            ("LIS Lab", "LIS-403", "CCS Building", "4th", 35),
            ("NAS Lab", "NAS-404", "CCS Building", "4th", 35),
        ]
        
        for name, code, building, floor, capacity in classrooms:
            cursor.execute('''
                INSERT INTO classrooms (name, code, building, floor, capacity)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, code, building, floor, capacity))
        
        self.conn.commit()
    
    def get_all_classrooms(self) -> List[Dict]:
        """Get all classrooms with their current schedule status"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.*,
                   rs.subject_name as current_subject,
                   rs.start_time || ' - ' || rs.end_time as current_time,
                   u.first_name || ' ' || u.last_name as instructor_name,
                   rs.id as schedule_id
            FROM classrooms c
            LEFT JOIN room_schedules rs ON c.id = rs.room_id 
                AND rs.schedule_date = date('now')
                AND rs.status = 'scheduled'
                AND time('now', 'localtime') BETWEEN rs.start_time AND rs.end_time
            LEFT JOIN users u ON rs.instructor_id = u.id
            ORDER BY c.name
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_classroom(self, room_id: int) -> Optional[Dict]:
        """Get classroom by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM classrooms WHERE id = ?', (room_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_classroom_by_code(self, code: str) -> Optional[Dict]:
        """Get classroom by code"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM classrooms WHERE code = ?', (code,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # ==================== ROOM SCHEDULE OPERATIONS ====================
    
    def create_room_schedule(self, room_id: int, instructor_id: int, subject_name: str,
                             schedule_date: str, start_time: str, end_time: str,
                             notes: str = "") -> Optional[int]:
        """Create a new room schedule/booking"""
        try:
            # Check for conflicts
            if self.check_schedule_conflict(room_id, schedule_date, start_time, end_time):
                return None
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO room_schedules (room_id, instructor_id, subject_name, 
                                           schedule_date, start_time, end_time, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (room_id, instructor_id, subject_name, schedule_date, start_time, end_time, notes))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def check_schedule_conflict(self, room_id: int, schedule_date: str, 
                                 start_time: str, end_time: str, exclude_id: int = None) -> bool:
        """Check if there's a scheduling conflict"""
        cursor = self.conn.cursor()
        query = '''
            SELECT COUNT(*) as count FROM room_schedules
            WHERE room_id = ? AND schedule_date = ? AND status = 'scheduled'
            AND ((start_time < ? AND end_time > ?) OR (start_time < ? AND end_time > ?)
                 OR (start_time >= ? AND end_time <= ?))
        '''
        params = [room_id, schedule_date, end_time, start_time, end_time, start_time, start_time, end_time]
        
        if exclude_id:
            query += ' AND id != ?'
            params.append(exclude_id)
        
        cursor.execute(query, params)
        return cursor.fetchone()['count'] > 0
    
    def get_room_schedules(self, room_id: int, date: str = None) -> List[Dict]:
        """Get schedules for a room"""
        cursor = self.conn.cursor()
        if date:
            cursor.execute('''
                SELECT rs.*, u.first_name || ' ' || u.last_name as instructor_name
                FROM room_schedules rs
                JOIN users u ON rs.instructor_id = u.id
                WHERE rs.room_id = ? AND rs.schedule_date = ? AND rs.status = 'scheduled'
                ORDER BY rs.start_time
            ''', (room_id, date))
        else:
            cursor.execute('''
                SELECT rs.*, u.first_name || ' ' || u.last_name as instructor_name
                FROM room_schedules rs
                JOIN users u ON rs.instructor_id = u.id
                WHERE rs.room_id = ? AND rs.status = 'scheduled'
                ORDER BY rs.schedule_date, rs.start_time
            ''', (room_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_instructor_schedules(self, instructor_id: int, date: str = None) -> List[Dict]:
        """Get all schedules for an instructor"""
        cursor = self.conn.cursor()
        if date:
            cursor.execute('''
                SELECT rs.*, c.name as room_name, c.code as room_code, c.building
                FROM room_schedules rs
                JOIN classrooms c ON rs.room_id = c.id
                WHERE rs.instructor_id = ? AND rs.schedule_date = ? AND rs.status = 'scheduled'
                ORDER BY rs.start_time
            ''', (instructor_id, date))
        else:
            cursor.execute('''
                SELECT rs.*, c.name as room_name, c.code as room_code, c.building
                FROM room_schedules rs
                JOIN classrooms c ON rs.room_id = c.id
                WHERE rs.instructor_id = ? AND rs.status = 'scheduled'
                ORDER BY rs.schedule_date, rs.start_time
            ''', (instructor_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_room_schedule(self, schedule_id: int, **kwargs) -> bool:
        """Update a room schedule"""
        allowed_fields = ['subject_name', 'schedule_date', 'start_time', 'end_time', 'notes', 'status']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
        values = list(updates.values()) + [schedule_id]
        
        cursor = self.conn.cursor()
        cursor.execute(f'UPDATE room_schedules SET {set_clause} WHERE id = ?', values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def cancel_room_schedule(self, schedule_id: int) -> bool:
        """Cancel a room schedule"""
        return self.update_room_schedule(schedule_id, status='cancelled')
    
    def delete_room_schedule(self, schedule_id: int) -> bool:
        """Delete a room schedule"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM room_schedules WHERE id = ?', (schedule_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_today_schedules(self) -> List[Dict]:
        """Get all schedules for today"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT rs.*, c.name as room_name, c.code as room_code, c.building,
                   u.first_name || ' ' || u.last_name as instructor_name
            FROM room_schedules rs
            JOIN classrooms c ON rs.room_id = c.id
            JOIN users u ON rs.instructor_id = u.id
            WHERE rs.schedule_date = date('now') AND rs.status = 'scheduled'
            ORDER BY rs.start_time
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Create global database instance
db = Database()


