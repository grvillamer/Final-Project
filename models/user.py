"""
User Model - Data Transfer Object
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """User data model"""
    id: int
    student_id: str
    email: str
    first_name: str
    last_name: str
    role: str = "student"  # student, instructor
    profile_image: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def initials(self) -> str:
        """Get initials from name"""
        first = self.first_name[0].upper() if self.first_name else ""
        last = self.last_name[0].upper() if self.last_name else ""
        return f"{first}{last}"
    
    @property
    def is_instructor(self) -> bool:
        """Check if user is an instructor"""
        return self.role == "instructor"
    
    @property
    def is_student(self) -> bool:
        """Check if user is a student"""
        return self.role == "student"
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create User from dictionary"""
        return cls(
            id=data.get('id', 0),
            student_id=data.get('student_id', ''),
            email=data.get('email', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', 'student'),
            profile_image=data.get('profile_image'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )
    
    def to_dict(self) -> dict:
        """Convert User to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'profile_image': self.profile_image,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }







