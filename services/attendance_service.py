"""
Attendance Service - Handles attendance tracking operations
"""
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from database import db
from models.attendance import AttendanceSession, AttendanceRecord
from utils.helpers import generate_qr_code


class AttendanceService:
    """Service for handling attendance operations"""
    
    @staticmethod
    def create_session(class_id: int, session_date: str = None,
                       expires_minutes: int = 30) -> Tuple[bool, Optional[AttendanceSession], str]:
        """
        Create a new attendance session
        Returns: (success, session, message)
        """
        if not session_date:
            session_date = datetime.now().strftime("%Y-%m-%d")
        
        qr_code = generate_qr_code()
        
        session_id = db.create_attendance_session(
            class_id=class_id,
            session_date=session_date,
            qr_code=qr_code,
            expires_minutes=expires_minutes
        )
        
        if session_id:
            session_data = db.get_attendance_session(session_id)
            return True, AttendanceSession.from_dict(session_data), "Session created"
        
        return False, None, "Failed to create attendance session"
    
    @staticmethod
    def get_or_create_today_session(class_id: int) -> Tuple[AttendanceSession, bool]:
        """
        Get today's session or create a new one
        Returns: (session, was_created)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        sessions = db.get_class_sessions(class_id)
        
        # Check if today's session exists
        for session in sessions:
            if session['session_date'] == today:
                return AttendanceSession.from_dict(session), False
        
        # Create new session
        success, session, _ = AttendanceService.create_session(class_id, today)
        return session, True
    
    @staticmethod
    def mark_attendance(session_id: int, student_id: int,
                        status: str = "present", notes: str = "") -> Tuple[bool, str]:
        """Mark student attendance for a session"""
        valid_statuses = ["present", "late", "absent", "excused"]
        if status not in valid_statuses:
            return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        
        success = db.mark_attendance(session_id, student_id, status, notes)
        
        if success:
            return True, f"Attendance marked as {status}"
        
        return False, "Failed to mark attendance"
    
    @staticmethod
    def mark_attendance_by_qr(qr_code: str, student_id: int) -> Tuple[bool, str]:
        """Mark attendance using QR code"""
        session = db.get_session_by_qr(qr_code)
        
        if not session:
            return False, "Invalid or expired attendance code"
        
        # Check if student is enrolled
        enrolled_classes = db.get_enrolled_classes(student_id)
        is_enrolled = any(c['id'] == session['class_id'] for c in enrolled_classes)
        
        if not is_enrolled:
            return False, "You are not enrolled in this class"
        
        return AttendanceService.mark_attendance(session['id'], student_id, "present")
    
    @staticmethod
    def get_session(session_id: int) -> Optional[AttendanceSession]:
        """Get attendance session by ID"""
        session_data = db.get_attendance_session(session_id)
        if session_data:
            return AttendanceSession.from_dict(session_data)
        return None
    
    @staticmethod
    def get_session_by_qr(qr_code: str) -> Optional[AttendanceSession]:
        """Get attendance session by QR code"""
        session_data = db.get_session_by_qr(qr_code)
        if session_data:
            return AttendanceSession.from_dict(session_data)
        return None
    
    @staticmethod
    def get_class_sessions(class_id: int) -> List[AttendanceSession]:
        """Get all sessions for a class"""
        sessions_data = db.get_class_sessions(class_id)
        return [AttendanceSession.from_dict(s) for s in sessions_data]
    
    @staticmethod
    def get_session_attendance(session_id: int) -> List[Dict]:
        """Get attendance records for a session"""
        return db.get_session_attendance(session_id)
    
    @staticmethod
    def get_student_history(student_id: int, class_id: int = None) -> List[Dict]:
        """Get attendance history for a student"""
        return db.get_student_attendance_history(student_id, class_id)
    
    @staticmethod
    def mark_all_present(session_id: int, class_id: int) -> Tuple[bool, int]:
        """Mark all students in a class as present"""
        students = db.get_class_students(class_id)
        count = 0
        
        for student in students:
            success = db.mark_attendance(session_id, student['id'], 'present')
            if success:
                count += 1
        
        return True, count
    
    @staticmethod
    def get_attendance_summary(session_id: int) -> Dict[str, int]:
        """Get attendance summary for a session"""
        records = db.get_session_attendance(session_id)
        
        summary = {
            'present': 0,
            'late': 0,
            'absent': 0,
            'excused': 0,
            'total': len(records)
        }
        
        for record in records:
            status = record.get('status', 'absent')
            if status in summary:
                summary[status] += 1
        
        return summary







