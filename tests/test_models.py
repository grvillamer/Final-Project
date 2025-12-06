"""
Unit Tests for Data Models
Tests: User, Class, Attendance models
"""
import unittest
from models.user import User
from models.classroom import Class, Enrollment
from models.attendance import AttendanceSession, AttendanceRecord
from models.settings import UserSettings


class TestUserModel(unittest.TestCase):
    """Tests for User model"""
    
    def test_user_from_dict(self):
        """Test creating User from dictionary"""
        data = {
            'id': 1,
            'student_id': 'STU001',
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'student'
        }
        
        user = User.from_dict(data)
        
        self.assertEqual(user.id, 1)
        self.assertEqual(user.student_id, 'STU001')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
    
    def test_user_full_name(self):
        """Test User full_name property"""
        user = User(
            id=1,
            student_id='STU001',
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.full_name, 'John Doe')
    
    def test_user_initials(self):
        """Test User initials property"""
        user = User(
            id=1,
            student_id='STU001',
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.initials, 'JD')
    
    def test_user_is_instructor(self):
        """Test User is_instructor property"""
        student = User(id=1, student_id='S1', email='s@test.com',
                       first_name='A', last_name='B', role='student')
        instructor = User(id=2, student_id='I1', email='i@test.com',
                          first_name='C', last_name='D', role='instructor')
        
        self.assertFalse(student.is_instructor)
        self.assertTrue(instructor.is_instructor)
    
    def test_user_to_dict(self):
        """Test User to_dict method"""
        user = User(
            id=1,
            student_id='STU001',
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        
        data = user.to_dict()
        
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['student_id'], 'STU001')
        self.assertEqual(data['first_name'], 'John')


class TestClassModel(unittest.TestCase):
    """Tests for Class model"""
    
    def test_class_from_dict(self):
        """Test creating Class from dictionary"""
        data = {
            'id': 1,
            'class_code': 'CS101',
            'name': 'Intro to Programming',
            'instructor_id': 1,
            'description': 'Basic programming',
            'schedule': 'MWF 9-10',
            'room': '301'
        }
        
        cls = Class.from_dict(data)
        
        self.assertEqual(cls.id, 1)
        self.assertEqual(cls.class_code, 'CS101')
        self.assertEqual(cls.name, 'Intro to Programming')
    
    def test_class_to_dict(self):
        """Test Class to_dict method"""
        cls = Class(
            id=1,
            class_code='CS101',
            name='Intro to Programming',
            instructor_id=1
        )
        
        data = cls.to_dict()
        
        self.assertEqual(data['class_code'], 'CS101')
        self.assertEqual(data['name'], 'Intro to Programming')


class TestAttendanceSessionModel(unittest.TestCase):
    """Tests for AttendanceSession model"""
    
    def test_attendance_rate_calculation(self):
        """Test attendance rate calculation"""
        session = AttendanceSession(
            id=1,
            class_id=1,
            session_date='2024-01-15',
            present_count=8,
            total_students=10
        )
        
        self.assertEqual(session.attendance_rate, 80.0)
    
    def test_attendance_rate_zero_students(self):
        """Test attendance rate with zero students"""
        session = AttendanceSession(
            id=1,
            class_id=1,
            session_date='2024-01-15',
            present_count=0,
            total_students=0
        )
        
        self.assertEqual(session.attendance_rate, 0.0)


class TestUserSettingsModel(unittest.TestCase):
    """Tests for UserSettings model"""
    
    def test_settings_from_dict(self):
        """Test creating UserSettings from dictionary"""
        data = {
            'dark_mode': 'true',
            'notifications': 'false',
            'language': 'en'
        }
        
        settings = UserSettings.from_dict(1, data)
        
        self.assertTrue(settings.dark_mode)
        self.assertFalse(settings.notifications)
        self.assertEqual(settings.language, 'en')
    
    def test_settings_to_dict(self):
        """Test UserSettings to_dict method"""
        settings = UserSettings(
            user_id=1,
            dark_mode=True,
            notifications=False,
            language='es'
        )
        
        data = settings.to_dict()
        
        self.assertEqual(data['dark_mode'], 'true')
        self.assertEqual(data['notifications'], 'false')
        self.assertEqual(data['language'], 'es')


if __name__ == '__main__':
    unittest.main()







