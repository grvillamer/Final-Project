"""
Attendance Models - Data Transfer Objects
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class AttendanceSession:
    """Attendance session data model"""
    id: int
    class_id: int
    session_date: str
    qr_code: str = ""
    status: str = "active"  # active, closed
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    present_count: int = 0
    total_students: int = 0
    
    @property
    def attendance_rate(self) -> float:
        """Calculate attendance rate percentage"""
        if self.total_students == 0:
            return 0.0
        return round((self.present_count / self.total_students) * 100, 1)
    
    @classmethod
    def from_dict(cls, data: dict) -> "AttendanceSession":
        """Create AttendanceSession from dictionary"""
        return cls(
            id=data.get('id', 0),
            class_id=data.get('class_id', 0),
            session_date=data.get('session_date', ''),
            qr_code=data.get('qr_code', ''),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            expires_at=data.get('expires_at'),
            present_count=data.get('present_count', 0),
            total_students=data.get('total_students', 0),
        )
    
    def to_dict(self) -> dict:
        """Convert AttendanceSession to dictionary"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'session_date': self.session_date,
            'qr_code': self.qr_code,
            'status': self.status,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'present_count': self.present_count,
            'total_students': self.total_students,
        }


@dataclass
class AttendanceRecord:
    """Individual attendance record data model"""
    id: int
    session_id: int
    student_id: int
    status: str = "absent"  # present, late, absent, excused
    marked_at: Optional[datetime] = None
    notes: str = ""
    
    # Student info (populated from joins)
    student_name: str = ""
    student_code: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> "AttendanceRecord":
        """Create AttendanceRecord from dictionary"""
        return cls(
            id=data.get('id', 0),
            session_id=data.get('session_id', 0),
            student_id=data.get('student_id', 0),
            status=data.get('status', 'absent'),
            marked_at=data.get('marked_at'),
            notes=data.get('notes', ''),
            student_name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
            student_code=data.get('student_id', ''),
        )
    
    def to_dict(self) -> dict:
        """Convert AttendanceRecord to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'student_id': self.student_id,
            'status': self.status,
            'marked_at': self.marked_at,
            'notes': self.notes,
        }







