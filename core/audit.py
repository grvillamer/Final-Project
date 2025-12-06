"""
Smart Classroom - Audit Logging Module
Implements comprehensive security audit logging
"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from config import config


class AuditLogger:
    """
    Security audit logger for tracking authentication and administrative actions.
    Logs to both file and database for compliance and forensics.
    """
    
    # Action types for categorization
    ACTION_TYPES = {
        # Authentication
        'LOGIN_SUCCESS': 'Authentication',
        'LOGIN_FAILED': 'Authentication',
        'LOGOUT': 'Authentication',
        'PASSWORD_CHANGE': 'Authentication',
        'PASSWORD_RESET_REQUEST': 'Authentication',
        'PASSWORD_RESET_COMPLETE': 'Authentication',
        'ACCOUNT_LOCKED': 'Authentication',
        'ACCOUNT_UNLOCKED': 'Authentication',
        
        # User Management
        'USER_CREATE': 'User Management',
        'USER_UPDATE': 'User Management',
        'USER_DELETE': 'User Management',
        'USER_DISABLE': 'User Management',
        'USER_ENABLE': 'User Management',
        'ROLE_CHANGE': 'User Management',
        
        # Profile
        'PROFILE_UPDATE': 'Profile',
        'PROFILE_PICTURE_CHANGE': 'Profile',
        
        # Session
        'SESSION_CREATE': 'Session',
        'SESSION_TIMEOUT': 'Session',
        'SESSION_INVALIDATE': 'Session',
        
        # Security
        'CSRF_VIOLATION': 'Security',
        'ACCESS_DENIED': 'Security',
        'SUSPICIOUS_ACTIVITY': 'Security',
        
        # System
        'SYSTEM_START': 'System',
        'SYSTEM_SHUTDOWN': 'System',
        'CONFIG_CHANGE': 'System',
        'BACKUP_CREATE': 'System',
        'BACKUP_RESTORE': 'System',
    }
    
    def __init__(self, db=None):
        self.db = db
        self._setup_file_logger()
    
    def _setup_file_logger(self):
        """Setup file-based logging"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # File handler for audit logs
        audit_file = log_dir / 'audit.log'
        file_handler = logging.FileHandler(audit_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Format: timestamp | level | action | user | details
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
        
        # Security log (critical events only)
        security_file = log_dir / 'security.log'
        security_handler = logging.FileHandler(security_file, encoding='utf-8')
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(formatter)
        
        self.security_logger = logging.getLogger('security')
        self.security_logger.setLevel(logging.WARNING)
        if not self.security_logger.handlers:
            self.security_logger.addHandler(security_handler)
    
    def log(self, action: str, user_id: Optional[int] = None, 
            username: str = None, details: Dict[str, Any] = None,
            ip_address: str = None, success: bool = True):
        """
        Log an audit event.
        
        Args:
            action: Action type (from ACTION_TYPES)
            user_id: ID of user performing action (if authenticated)
            username: Username for display
            details: Additional details as dict
            ip_address: Client IP address
            success: Whether action was successful
        """
        category = self.ACTION_TYPES.get(action, 'Unknown')
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'category': category,
            'user_id': user_id,
            'username': username or 'Anonymous',
            'success': success,
            'ip_address': ip_address,
            'details': details or {}
        }
        
        # Format for file logging
        details_str = json.dumps(details) if details else ''
        log_message = f"{action} | user={username or 'Anonymous'}(id={user_id}) | success={success} | {details_str}"
        
        # Log to file
        if success:
            self.logger.info(log_message)
        else:
            self.logger.warning(log_message)
        
        # Log security events separately
        if action in ['LOGIN_FAILED', 'ACCOUNT_LOCKED', 'CSRF_VIOLATION', 
                      'ACCESS_DENIED', 'SUSPICIOUS_ACTIVITY']:
            self.security_logger.warning(log_message)
        
        # Log to database if available
        if self.db:
            try:
                self.db.add_audit_log(
                    action=action,
                    category=category,
                    user_id=user_id,
                    username=username,
                    success=success,
                    ip_address=ip_address,
                    details=json.dumps(details) if details else None
                )
            except Exception as e:
                self.logger.error(f"Failed to write audit log to database: {e}")
    
    # ==================== CONVENIENCE METHODS ====================
    
    def log_login_success(self, user_id: int, username: str, ip: str = None):
        """Log successful login"""
        self.log('LOGIN_SUCCESS', user_id, username, 
                 {'message': 'User logged in successfully'}, ip, True)
    
    def log_login_failed(self, username: str, reason: str, ip: str = None):
        """Log failed login attempt"""
        self.log('LOGIN_FAILED', None, username,
                 {'reason': reason}, ip, False)
    
    def log_logout(self, user_id: int, username: str):
        """Log user logout"""
        self.log('LOGOUT', user_id, username,
                 {'message': 'User logged out'}, None, True)
    
    def log_password_change(self, user_id: int, username: str, forced: bool = False):
        """Log password change"""
        self.log('PASSWORD_CHANGE', user_id, username,
                 {'forced': forced, 'message': 'Password changed'}, None, True)
    
    def log_user_create(self, admin_id: int, admin_name: str, 
                        new_user_id: int, new_username: str, role: str):
        """Log user creation by admin"""
        self.log('USER_CREATE', admin_id, admin_name,
                 {'new_user_id': new_user_id, 'new_username': new_username, 'role': role},
                 None, True)
    
    def log_user_delete(self, admin_id: int, admin_name: str,
                        deleted_user_id: int, deleted_username: str):
        """Log user deletion by admin"""
        self.log('USER_DELETE', admin_id, admin_name,
                 {'deleted_user_id': deleted_user_id, 'deleted_username': deleted_username},
                 None, True)
    
    def log_role_change(self, admin_id: int, admin_name: str,
                        target_user_id: int, target_username: str,
                        old_role: str, new_role: str):
        """Log role change by admin"""
        self.log('ROLE_CHANGE', admin_id, admin_name,
                 {'target_user_id': target_user_id, 'target_username': target_username,
                  'old_role': old_role, 'new_role': new_role},
                 None, True)
    
    def log_account_locked(self, username: str, attempts: int, ip: str = None):
        """Log account lockout"""
        self.log('ACCOUNT_LOCKED', None, username,
                 {'failed_attempts': attempts, 'message': 'Account locked due to failed attempts'},
                 ip, False)
    
    def log_access_denied(self, user_id: int, username: str, 
                          resource: str, required_role: str):
        """Log access denied event"""
        self.log('ACCESS_DENIED', user_id, username,
                 {'resource': resource, 'required_role': required_role},
                 None, False)


# Create global audit logger (will be initialized with db later)
audit_logger = AuditLogger()

