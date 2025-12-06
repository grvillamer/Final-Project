"""
SpottEd Database Service - Offline-First SQLite Storage
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import hashlib


class Database:
    """SQLite database service with offline-first capabilities"""
    
    def __init__(self, db_path: str = "spotted.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create all required tables"""
        cursor = self.conn.cursor()
        
        # Users table
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
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, student_id: str, email: str, password: str, 
                    first_name: str, last_name: str, role: str = "student") -> Optional[int]:
        """Create a new user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO users (student_id, email, password_hash, first_name, last_name, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, email, self._hash_password(password), first_name, last_name, role))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def authenticate_user(self, student_id: str, password: str) -> Optional[Dict]:
        """Authenticate user by student ID and password"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM users WHERE student_id = ? AND password_hash = ?
        ''', (student_id, self._hash_password(password)))
        row = cursor.fetchone()
        return dict(row) if row else None
    
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
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (self._hash_password(new_password), user_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
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


