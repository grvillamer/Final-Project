"""
Smart Classroom - Security Service Module
Implements secure password handling, validation, and authentication controls
"""
import re
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
import hashlib

# Try to use bcrypt for password hashing (recommended)
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    print("[SECURITY] WARNING: bcrypt not available, using SHA-256 fallback")

from config import config


class PasswordPolicy:
    """
    Password policy enforcement with configurable rules.
    Implements NIST 800-63B guidelines.
    """
    
    def __init__(self):
        self.min_length = config.PASSWORD_MIN_LENGTH
        self.require_uppercase = config.PASSWORD_REQUIRE_UPPERCASE
        self.require_lowercase = config.PASSWORD_REQUIRE_LOWERCASE
        self.require_digit = config.PASSWORD_REQUIRE_DIGIT
        self.require_special = config.PASSWORD_REQUIRE_SPECIAL
        self.history_count = config.PASSWORD_HISTORY_COUNT
        
        # Common weak passwords to block
        self.common_passwords = {
            'password', 'password123', '123456', '12345678', 'qwerty',
            'abc123', 'monkey', 'master', 'dragon', 'letmein',
            'login', 'admin', 'welcome', 'solo', 'princess',
            'starwars', 'passw0rd', 'p@ssword', 'p@ssw0rd'
        }
    
    def validate(self, password: str, username: str = None) -> Tuple[bool, List[str]]:
        """
        Validate password against policy.
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        # Length check
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")
        
        # Uppercase check
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Lowercase check
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Digit check
        if self.require_digit and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        # Special character check
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*)")
        
        # Common password check
        if password.lower() in self.common_passwords:
            errors.append("This password is too common. Please choose a stronger password")
        
        # Username in password check
        if username and username.lower() in password.lower():
            errors.append("Password cannot contain your username")
        
        # Sequential characters check
        if self._has_sequential_chars(password):
            errors.append("Password cannot contain sequential characters (abc, 123)")
        
        return len(errors) == 0, errors
    
    def _has_sequential_chars(self, password: str, seq_length: int = 3) -> bool:
        """Check for sequential characters"""
        sequences = [
            'abcdefghijklmnopqrstuvwxyz',
            '0123456789',
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]
        
        password_lower = password.lower()
        for seq in sequences:
            for i in range(len(seq) - seq_length + 1):
                if seq[i:i+seq_length] in password_lower:
                    return True
                # Check reverse
                if seq[i:i+seq_length][::-1] in password_lower:
                    return True
        return False
    
    def get_strength(self, password: str) -> Tuple[int, str]:
        """
        Calculate password strength score (0-100) and label.
        """
        score = 0
        
        # Length scoring
        length = len(password)
        if length >= 8: score += 20
        if length >= 12: score += 15
        if length >= 16: score += 10
        
        # Character variety
        if re.search(r'[a-z]', password): score += 10
        if re.search(r'[A-Z]', password): score += 15
        if re.search(r'\d', password): score += 15
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password): score += 15
        
        # Bonus for mixing
        char_types = sum([
            bool(re.search(r'[a-z]', password)),
            bool(re.search(r'[A-Z]', password)),
            bool(re.search(r'\d', password)),
            bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        ])
        if char_types >= 3: score += 10
        if char_types == 4: score += 10
        
        # Penalize common patterns
        if password.lower() in self.common_passwords:
            score = min(score, 10)
        
        # Determine label
        if score >= 80:
            label = "Strong"
        elif score >= 60:
            label = "Good"
        elif score >= 40:
            label = "Fair"
        else:
            label = "Weak"
        
        return min(score, 100), label


class SecurityService:
    """
    Core security service for authentication and access control.
    """
    
    def __init__(self):
        self.password_policy = PasswordPolicy()
        self.max_login_attempts = config.MAX_LOGIN_ATTEMPTS
        self.lockout_duration = config.LOCKOUT_DURATION_MINUTES
    
    # ==================== PASSWORD HASHING ====================
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt (preferred) or SHA-256 fallback.
        Returns the hash string.
        """
        if BCRYPT_AVAILABLE:
            # Use bcrypt with cost factor 12 (recommended for 2024)
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        else:
            # Fallback to SHA-256 with salt (less secure but functional)
            salt = secrets.token_hex(16)
            hash_obj = hashlib.sha256((salt + password).encode())
            return f"sha256${salt}${hash_obj.hexdigest()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify password against stored hash.
        Supports both bcrypt and SHA-256 formats.
        """
        try:
            if hashed.startswith('$2'):
                # bcrypt hash
                if BCRYPT_AVAILABLE:
                    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
                return False
            elif hashed.startswith('sha256$'):
                # SHA-256 fallback format
                parts = hashed.split('$')
                if len(parts) == 3:
                    salt = parts[1]
                    stored_hash = parts[2]
                    computed = hashlib.sha256((salt + password).encode()).hexdigest()
                    return secrets.compare_digest(computed, stored_hash)
            else:
                # Legacy SHA-256 (no salt) - for migration
                legacy_hash = hashlib.sha256(password.encode()).hexdigest()
                return secrets.compare_digest(legacy_hash, hashed)
        except Exception:
            return False
    
    # ==================== TOKEN GENERATION ====================
    
    def generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def generate_reset_token(self) -> str:
        """Generate a secure password reset token"""
        return secrets.token_urlsafe(48)
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF protection token"""
        return secrets.token_hex(32)
    
    # ==================== ACCOUNT LOCKOUT ====================
    
    def is_account_locked(self, failed_attempts: int, last_failed: datetime) -> Tuple[bool, int]:
        """
        Check if account is locked due to failed attempts.
        Returns (is_locked, minutes_remaining)
        """
        if failed_attempts < self.max_login_attempts:
            return False, 0
        
        lockout_end = last_failed + timedelta(minutes=self.lockout_duration)
        now = datetime.now()
        
        if now < lockout_end:
            remaining = int((lockout_end - now).total_seconds() / 60) + 1
            return True, remaining
        
        return False, 0
    
    # ==================== INPUT VALIDATION ====================
    
    def sanitize_input(self, value: str, max_length: int = 255) -> str:
        """
        Sanitize user input to prevent injection attacks.
        """
        if not value:
            return ""
        
        # Trim and limit length
        value = value.strip()[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Basic HTML entity encoding for display
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        value = value.replace('"', '&quot;')
        value = value.replace("'", '&#x27;')
        
        return value
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_student_id(self, student_id: str) -> bool:
        """Validate student ID format"""
        # Allow alphanumeric with optional dashes
        pattern = r'^[A-Za-z0-9\-]{3,20}$'
        return bool(re.match(pattern, student_id))


# Create global security service instance
security_service = SecurityService()
password_policy = PasswordPolicy()

