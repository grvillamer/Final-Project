"""
Authentication Service - Handles user authentication and session management
"""
import hashlib
from typing import Optional, Tuple
from database import db
from models.user import User


class AuthService:
    """Service for handling authentication operations"""
    
    _current_user: Optional[User] = None
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = "spotted_salt_2024"
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    
    @classmethod
    def login(cls, student_id: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate user with student ID and password
        Returns: (success, user, message)
        """
        if not student_id or not password:
            return False, None, "Student ID and password are required"
        
        user_data = db.authenticate_user(student_id, password)
        
        if user_data:
            cls._current_user = User.from_dict(user_data)
            return True, cls._current_user, "Login successful"
        
        return False, None, "Invalid Student ID or password"
    
    @classmethod
    def register(cls, student_id: str, email: str, password: str,
                 first_name: str, last_name: str, role: str = "student") -> Tuple[bool, Optional[User], str]:
        """
        Register a new user
        Returns: (success, user, message)
        """
        # Validation
        if not student_id:
            return False, None, "Student ID is required"
        if not email:
            return False, None, "Email is required"
        if not password or len(password) < 6:
            return False, None, "Password must be at least 6 characters"
        if not first_name:
            return False, None, "First name is required"
        if not last_name:
            return False, None, "Last name is required"
        
        # Check for existing user
        existing = db.get_user_by_email(email)
        if existing:
            return False, None, "Email already registered"
        
        # Create user
        user_id = db.create_user(
            student_id=student_id,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        if user_id:
            user_data = db.get_user(user_id)
            cls._current_user = User.from_dict(user_data)
            return True, cls._current_user, "Registration successful"
        
        return False, None, "Student ID or email already exists"
    
    @classmethod
    def logout(cls) -> bool:
        """Log out the current user"""
        cls._current_user = None
        return True
    
    @classmethod
    def get_current_user(cls) -> Optional[User]:
        """Get the currently logged in user"""
        return cls._current_user
    
    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if a user is currently authenticated"""
        return cls._current_user is not None
    
    @classmethod
    def update_profile(cls, first_name: str = None, last_name: str = None,
                       email: str = None) -> Tuple[bool, str]:
        """Update current user's profile"""
        if not cls._current_user:
            return False, "Not authenticated"
        
        updates = {}
        if first_name:
            updates['first_name'] = first_name
        if last_name:
            updates['last_name'] = last_name
        if email:
            updates['email'] = email
        
        if not updates:
            return False, "No updates provided"
        
        success = db.update_user(cls._current_user.id, **updates)
        
        if success:
            # Refresh user data
            user_data = db.get_user(cls._current_user.id)
            cls._current_user = User.from_dict(user_data)
            return True, "Profile updated successfully"
        
        return False, "Failed to update profile"
    
    @classmethod
    def change_password(cls, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change current user's password"""
        if not cls._current_user:
            return False, "Not authenticated"
        
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters"
        
        # Verify old password
        user_data = db.authenticate_user(cls._current_user.student_id, old_password)
        if not user_data:
            return False, "Current password is incorrect"
        
        success = db.update_password(cls._current_user.id, new_password)
        
        if success:
            return True, "Password changed successfully"
        
        return False, "Failed to change password"
    
    @classmethod
    def reset_password(cls, email: str, new_password: str) -> Tuple[bool, str]:
        """Reset password by email"""
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters"
        
        user_data = db.get_user_by_email(email)
        if not user_data:
            return False, "No account found with this email"
        
        success = db.update_password(user_data['id'], new_password)
        
        if success:
            return True, "Password reset successfully"
        
        return False, "Failed to reset password"







