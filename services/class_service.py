"""
Class Service - Handles class/course management operations
"""
from typing import List, Optional, Tuple
from database import db
from models.classroom import Class, Enrollment
from models.user import User
from utils.helpers import generate_class_code


class ClassService:
    """Service for handling class management operations"""
    
    @staticmethod
    def create_class(instructor_id: int, name: str, description: str = "",
                     schedule: str = "", room: str = "") -> Tuple[bool, Optional[Class], str]:
        """
        Create a new class
        Returns: (success, class, message)
        """
        if not name:
            return False, None, "Class name is required"
        
        class_code = generate_class_code()
        
        class_id = db.create_class(
            class_code=class_code,
            name=name,
            instructor_id=instructor_id,
            description=description,
            schedule=schedule,
            room=room
        )
        
        if class_id:
            class_data = db.get_class(class_id)
            return True, Class.from_dict(class_data), "Class created successfully"
        
        return False, None, "Failed to create class"
    
    @staticmethod
    def update_class(class_id: int, name: str = None, description: str = None,
                     schedule: str = None, room: str = None) -> Tuple[bool, str]:
        """Update class information"""
        updates = {}
        if name is not None:
            updates['name'] = name
        if description is not None:
            updates['description'] = description
        if schedule is not None:
            updates['schedule'] = schedule
        if room is not None:
            updates['room'] = room
        
        if not updates:
            return False, "No updates provided"
        
        success = db.update_class(class_id, **updates)
        
        if success:
            return True, "Class updated successfully"
        
        return False, "Failed to update class"
    
    @staticmethod
    def delete_class(class_id: int) -> Tuple[bool, str]:
        """Delete a class and all related data"""
        success = db.delete_class(class_id)
        
        if success:
            return True, "Class deleted successfully"
        
        return False, "Failed to delete class"
    
    @staticmethod
    def get_class(class_id: int) -> Optional[Class]:
        """Get class by ID"""
        class_data = db.get_class(class_id)
        if class_data:
            return Class.from_dict(class_data)
        return None
    
    @staticmethod
    def get_class_by_code(class_code: str) -> Optional[Class]:
        """Get class by code"""
        cursor = db.conn.cursor()
        cursor.execute('SELECT * FROM classes WHERE class_code = ?', (class_code.upper(),))
        row = cursor.fetchone()
        if row:
            return Class.from_dict(dict(row))
        return None
    
    @staticmethod
    def get_instructor_classes(instructor_id: int) -> List[Class]:
        """Get all classes for an instructor"""
        classes_data = db.get_classes_by_instructor(instructor_id)
        return [Class.from_dict(c) for c in classes_data]
    
    @staticmethod
    def get_enrolled_classes(student_id: int) -> List[Class]:
        """Get all classes a student is enrolled in"""
        classes_data = db.get_enrolled_classes(student_id)
        return [Class.from_dict(c) for c in classes_data]
    
    @staticmethod
    def enroll_student(class_code: str, student_id: int) -> Tuple[bool, str]:
        """Enroll a student in a class by class code"""
        # Find class
        cls = ClassService.get_class_by_code(class_code)
        if not cls:
            return False, "Class not found"
        
        success = db.enroll_student(cls.id, student_id)
        
        if success:
            return True, f"Successfully enrolled in {cls.name}"
        
        return False, "Already enrolled in this class"
    
    @staticmethod
    def unenroll_student(class_id: int, student_id: int) -> Tuple[bool, str]:
        """Remove a student from a class"""
        success = db.unenroll_student(class_id, student_id)
        
        if success:
            return True, "Successfully unenrolled from class"
        
        return False, "Failed to unenroll from class"
    
    @staticmethod
    def get_class_students(class_id: int) -> List[dict]:
        """Get all students in a class"""
        return db.get_class_students(class_id)
    
    @staticmethod
    def get_class_count(instructor_id: int = None, student_id: int = None) -> int:
        """Get count of classes"""
        if instructor_id:
            return len(db.get_classes_by_instructor(instructor_id))
        elif student_id:
            return len(db.get_enrolled_classes(student_id))
        return 0







