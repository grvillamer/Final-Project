"""
Unit Tests for Services
Tests: AuthService, ClassService, AttendanceService, AnalyticsService
"""
import unittest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from services.auth_service import AuthService
from services.class_service import ClassService
from services.attendance_service import AttendanceService
from services.analytics_service import AnalyticsService
from services.sync_service import SyncService


class TestAuthService(unittest.TestCase):
    """Tests for Authentication Service"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database"""
        cls.test_db_path = 'test_spotted.db'
        # Create fresh test database
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        
        # Initialize database
        import database
        database.db = Database(cls.test_db_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        import database
        database.db.close()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
    
    def test_register_user(self):
        """Test user registration"""
        success, user, message = AuthService.register(
            student_id='TEST001',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            role='student'
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.student_id, 'TEST001')
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email fails"""
        # First registration
        AuthService.register(
            student_id='TEST002',
            email='duplicate@example.com',
            password='password123',
            first_name='Test',
            last_name='One'
        )
        
        # Duplicate registration
        success, user, message = AuthService.register(
            student_id='TEST003',
            email='duplicate@example.com',
            password='password123',
            first_name='Test',
            last_name='Two'
        )
        
        self.assertFalse(success)
        self.assertIn('already', message.lower())
    
    def test_login_success(self):
        """Test successful login"""
        # Register first
        AuthService.register(
            student_id='LOGIN001',
            email='login@example.com',
            password='mypassword',
            first_name='Login',
            last_name='Test'
        )
        
        # Then login
        success, user, message = AuthService.login('LOGIN001', 'mypassword')
        
        self.assertTrue(success)
        self.assertIsNotNone(user)
    
    def test_login_invalid_password(self):
        """Test login with invalid password"""
        success, user, message = AuthService.login('LOGIN001', 'wrongpassword')
        
        self.assertFalse(success)
        self.assertIsNone(user)
    
    def test_password_validation(self):
        """Test password validation"""
        success, user, message = AuthService.register(
            student_id='PASS001',
            email='pass@example.com',
            password='123',  # Too short
            first_name='Pass',
            last_name='Test'
        )
        
        self.assertFalse(success)
        self.assertIn('6 characters', message)


class TestClassService(unittest.TestCase):
    """Tests for Class Service"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and user"""
        cls.test_db_path = 'test_class_service.db'
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        
        import database
        database.db = Database(cls.test_db_path)
        
        # Create test instructor
        database.db.create_user(
            student_id='INST001',
            email='instructor@test.com',
            password='password',
            first_name='Test',
            last_name='Instructor',
            role='instructor'
        )
        cls.instructor_id = 1
    
    @classmethod
    def tearDownClass(cls):
        import database
        database.db.close()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
    
    def test_create_class(self):
        """Test class creation"""
        success, cls, message = ClassService.create_class(
            instructor_id=self.instructor_id,
            name='Test Class',
            description='A test class',
            schedule='MWF 9-10',
            room='101'
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(cls)
        self.assertEqual(cls.name, 'Test Class')
        self.assertIsNotNone(cls.class_code)
    
    def test_create_class_no_name(self):
        """Test class creation fails without name"""
        success, cls, message = ClassService.create_class(
            instructor_id=self.instructor_id,
            name='',
            description='No name'
        )
        
        self.assertFalse(success)
    
    def test_get_instructor_classes(self):
        """Test getting instructor's classes"""
        ClassService.create_class(
            instructor_id=self.instructor_id,
            name='Another Class'
        )
        
        classes = ClassService.get_instructor_classes(self.instructor_id)
        
        self.assertGreater(len(classes), 0)


class TestAnalyticsService(unittest.TestCase):
    """Tests for Analytics Service (AI Features)"""
    
    def test_predict_attendance_empty_data(self):
        """Test prediction with empty data"""
        from utils.helpers import predict_attendance
        
        result = predict_attendance([])
        
        self.assertEqual(result['predicted_rate'], 0)
        self.assertEqual(result['confidence'], 0)
    
    def test_identify_at_risk_students(self):
        """Test at-risk student identification"""
        from utils.helpers import identify_at_risk_students
        
        students = [
            {'first_name': 'Good', 'last_name': 'Student', 'present_count': 9, 'late_count': 1, 'total_sessions': 10},
            {'first_name': 'At', 'last_name': 'Risk', 'present_count': 5, 'late_count': 0, 'total_sessions': 10},
        ]
        
        at_risk = identify_at_risk_students(students, threshold=75.0)
        
        self.assertEqual(len(at_risk), 1)
        self.assertEqual(at_risk[0]['first_name'], 'At')
    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        from utils.helpers import generate_recommendations
        
        analytics = {
            'overall_attendance_rate': 65,
            'trend': 'declining',
            'students_data': []
        }
        
        recommendations = generate_recommendations(analytics)
        
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any('attendance' in r.lower() for r in recommendations))
    
    def test_calculate_trend(self):
        """Test trend calculation"""
        from utils.helpers import calculate_trend
        
        # Improving trend
        improving_data = [70, 75, 80, 85, 90]
        trend, slope = calculate_trend(improving_data)
        self.assertEqual(trend, 'improving')
        
        # Declining trend
        declining_data = [90, 85, 80, 75, 70]
        trend, slope = calculate_trend(declining_data)
        self.assertEqual(trend, 'declining')


class TestSyncService(unittest.TestCase):
    """Tests for Sync Service (Offline-First Feature)"""
    
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = 'test_sync_service.db'
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        
        import database
        database.db = Database(cls.test_db_path)
    
    @classmethod
    def tearDownClass(cls):
        import database
        database.db.close()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
    
    def test_queue_operation(self):
        """Test queuing a sync operation"""
        SyncService.queue_operation(
            operation='INSERT',
            table_name='attendance_records',
            data={'session_id': 1, 'student_id': 1, 'status': 'present'}
        )
        
        pending = SyncService.get_pending_operations()
        self.assertGreater(len(pending), 0)
    
    def test_get_sync_status(self):
        """Test getting sync status"""
        status = SyncService.get_sync_status()
        
        self.assertIn('is_online', status)
        self.assertIn('pending_operations', status)
        self.assertIn('status', status)
    
    def test_conflict_resolution_local_wins(self):
        """Test conflict resolution - local wins"""
        local = {'name': 'Local Name', 'updated_at': '2024-01-02'}
        remote = {'name': 'Remote Name', 'updated_at': '2024-01-01'}
        
        result = SyncService.resolve_conflict(local, remote, 'local_wins')
        
        self.assertEqual(result['name'], 'Local Name')
    
    def test_conflict_resolution_newest_wins(self):
        """Test conflict resolution - newest wins"""
        local = {'name': 'Local Name', 'updated_at': '2024-01-01'}
        remote = {'name': 'Remote Name', 'updated_at': '2024-01-02'}
        
        result = SyncService.resolve_conflict(local, remote, 'newest_wins')
        
        self.assertEqual(result['name'], 'Remote Name')


if __name__ == '__main__':
    unittest.main()







