"""
Class and Enrollment Models - Data Transfer Objects
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Class:
    """Class/Course data model"""
    id: int
    class_code: str
    name: str
    instructor_id: int
    description: str = ""
    schedule: str = ""
    room: str = ""
    student_count: int = 0
    created_at: Optional[datetime] = None
    instructor_name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Class":
        """Create Class from dictionary"""
        return cls(
            id=data.get('id', 0),
            class_code=data.get('class_code', ''),
            name=data.get('name', ''),
            instructor_id=data.get('instructor_id', 0),
            description=data.get('description', ''),
            schedule=data.get('schedule', ''),
            room=data.get('room', ''),
            student_count=data.get('student_count', 0),
            created_at=data.get('created_at'),
            instructor_name=data.get('instructor_name'),
        )
    
    def to_dict(self) -> dict:
        """Convert Class to dictionary"""
        return {
            'id': self.id,
            'class_code': self.class_code,
            'name': self.name,
            'instructor_id': self.instructor_id,
            'description': self.description,
            'schedule': self.schedule,
            'room': self.room,
            'student_count': self.student_count,
            'created_at': self.created_at,
            'instructor_name': self.instructor_name,
        }


@dataclass
class Enrollment:
    """Enrollment data model"""
    id: int
    class_id: int
    student_id: int
    enrolled_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Enrollment":
        """Create Enrollment from dictionary"""
        return cls(
            id=data.get('id', 0),
            class_id=data.get('class_id', 0),
            student_id=data.get('student_id', 0),
            enrolled_at=data.get('enrolled_at'),
        )
    
    def to_dict(self) -> dict:
        """Convert Enrollment to dictionary"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'student_id': self.student_id,
            'enrolled_at': self.enrolled_at,
        }







