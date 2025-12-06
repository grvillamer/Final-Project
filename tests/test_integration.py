"""
Integration Tests for SpottEd Application
Tests: Complete user flows and feature integrations
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database


class TestUserRegistrationLoginFlow(unittest.TestCase):
    """
    Integration Test: Complete registration and login flow
    Tests the full lifecycle from registration to login to profile update
    """
    
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = 'test_integration_auth.db'
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
    
    def test_complete_auth_flow(self):
        """Test complete authentication flow"""
        from services.auth_service import AuthService
        
        # Step 1: Register new user
        success, user, message = AuthService.register(
            student_id='FLOW001',
            email='flowtest@example.com',
            password='testpassword',
            first_name='Flow',
            last_name='Test',
            role='instructor'
        )
        self.assertTrue(success, "Registration should succeed")
        self.assertEqual(user.student_id, 'FLOW001')
        
        # Step 2: Logout
        AuthService.logout()
        self.assertIsNone(AuthService.get_current_user())
        
        # Step 3: Login with registered credentials
        success, user, message = AuthService.login('FLOW001', 'testpassword')
        self.assertTrue(success, "Login should succeed")
        self.assertEqual(user.email, 'flowtest@example.com')
        
        # Step 4: Update profile
        success, message = AuthService.update_profile(
            first_name='Updated',
            last_name='Name'
        )
        self.assertTrue(success, "Profile update should succeed")
        
        # Step 5: Verify update
        current_user = AuthService.get_current_user()
        self.assertEqual(current_user.first_name, 'Updated')
        self.assertEqual(current_user.last_name, 'Name')


class TestClassManagementFlow(unittest.TestCase):
    """
    Integration Test: Complete class management flow
    Tests creating class, enrolling students, and viewing class data
    """
    
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = 'test_integration_class.db'
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        
        import database
        database.db = Database(cls.test_db_path)
        
        # Create instructor and students
        cls.instructor_id = database.db.create_user(
            'INST100', 'inst@test.com', 'pass', 'Test', 'Instructor', 'instructor'
        )
        cls.student_id = database.db.create_user(
            'STU100', 'stu@test.com', 'pass', 'Test', 'Student', 'student'
        )
    
    @classmethod
    def tearDownClass(cls):
        import database
        database.db.close()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
    
    def test_complete_class_flow(self):
        """Test complete class management flow"""
        from services.class_service import ClassService
        
        # Step 1: Create class
        success, cls, message = ClassService.create_class(
            instructor_id=self.instructor_id,
            name='Integration Test Class',
            description='Testing class flow',
            schedule='TTH 2-3',
            room='201'
        )
        self.assertTrue(success)
        class_id = cls.id
        class_code = cls.class_code
        
        # Step 2: Get class by code
        found_class = ClassService.get_class_by_code(class_code)
        self.assertIsNotNone(found_class)
        self.assertEqual(found_class.name, 'Integration Test Class')
        
        # Step 3: Enroll student
        success, message = ClassService.enroll_student(class_code, self.student_id)
        self.assertTrue(success)
        
        # Step 4: Verify enrollment
        students = ClassService.get_class_students(class_id)
        self.assertEqual(len(students), 1)
        
        # Step 5: Get enrolled classes for student
        enrolled = ClassService.get_enrolled_classes(self.student_id)
        self.assertEqual(len(enrolled), 1)
        self.assertEqual(enrolled[0].name, 'Integration Test Class')
        
        # Step 6: Update class
        success, message = ClassService.update_class(
            class_id,
            name='Updated Class Name',
            room='302'
        )
        self.assertTrue(success)
        
        # Step 7: Verify update
        updated_class = ClassService.get_class(class_id)
        self.assertEqual(updated_class.name, 'Updated Class Name')
        self.assertEqual(updated_class.room, '302')


class TestAttendanceWorkflow(unittest.TestCase):
    """
    Integration Test: Complete attendance tracking workflow
    Tests session creation, attendance marking, and history retrieval
    """
    
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = 'test_integration_attendance.db'
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        
        import database
        database.db = Database(cls.test_db_path)
        
        # Create instructor, student, and class
        cls.instructor_id = database.db.create_user(
            'INST200', 'inst2@test.com', 'pass', 'Test', 'Instructor', 'instructor'
        )
        cls.student_id = database.db.create_user(
            'STU200', 'stu2@test.com', 'pass', 'Test', 'Student', 'student'
        )
        cls.class_id = database.db.create_class(
            'ATT101', 'Attendance Test', '', cls.instructor_id, '', ''
        )
        database.db.enroll_student(cls.class_id, cls.student_id)
    
    @classmethod
    def tearDownClass(cls):
        import database
        database.db.close()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
    
    def test_complete_attendance_flow(self):
        """Test complete attendance tracking flow"""
        from services.attendance_service import AttendanceService
        
        # Step 1: Create attendance session
        success, session, message = AttendanceService.create_session(
            class_id=self.class_id,
            session_date='2024-01-15'
        )
        self.assertTrue(success)
        session_id = session.id
        qr_code = session.qr_code
        
        # Step 2: Get session by QR code
        found_session = AttendanceService.get_session_by_qr(qr_code)
        self.assertIsNotNone(found_session)
        
        # Step 3: Mark attendance via QR code
        success, message = AttendanceService.mark_attendance_by_qr(
            qr_code, self.student_id
        )
        self.assertTrue(success)
        
        # Step 4: Get session attendance
        attendance = AttendanceService.get_session_attendance(session_id)
        self.assertEqual(len(attendance), 1)
        self.assertEqual(attendance[0]['status'], 'present')
        
        # Step 5: Get student history
        history = AttendanceService.get_student_history(self.student_id)
        self.assertGreater(len(history), 0)
        
        # Step 6: Get attendance summary
        summary = AttendanceService.get_attendance_summary(session_id)
        self.assertEqual(summary['present'], 1)
        self.assertEqual(summary['total'], 1)


class TestAnalyticsWorkflow(unittest.TestCase):
    """
    Integration Test: AI Analytics workflow
    Tests emerging technology feature - analytics and predictions
    """
    
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = 'test_integration_analytics.db'
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        
        import database
        database.db = Database(cls.test_db_path)
        
        # Create test data
        cls.instructor_id = database.db.create_user(
            'INST300', 'inst3@test.com', 'pass', 'Test', 'Instructor', 'instructor'
        )
        
        # Create students
        cls.student_ids = []
        for i in range(5):
            sid = database.db.create_user(
                f'STU30{i}', f'stu30{i}@test.com', 'pass',
                f'Student{i}', 'Test', 'student'
            )
            cls.student_ids.append(sid)
        
        # Create class
        cls.class_id = database.db.create_class(
            'ANA101', 'Analytics Test', '', cls.instructor_id, '', ''
        )
        
        # Enroll students
        for sid in cls.student_ids:
            database.db.enroll_student(cls.class_id, sid)
        
        # Create attendance sessions with varied attendance
        import random
        for day in range(1, 8):
            session_id = database.db.create_attendance_session(
                cls.class_id, f'2024-01-{day:02d}'
            )
            for i, sid in enumerate(cls.student_ids):
                # Vary attendance - first 3 students have good attendance
                if i < 3:
                    status = random.choice(['present', 'present', 'present', 'late'])
                else:
                    status = random.choice(['present', 'absent', 'absent', 'late'])
                database.db.mark_attendance(session_id, sid, status)
    
    @classmethod
    def tearDownClass(cls):
        import database
        database.db.close()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
    
    def test_complete_analytics_flow(self):
        """Test complete analytics workflow"""
        from services.analytics_service import AnalyticsService
        
        # Step 1: Get class analytics
        analytics = AnalyticsService.get_class_analytics(self.class_id)
        self.assertIn('total_sessions', analytics)
        self.assertIn('prediction', analytics)
        self.assertIn('recommendations', analytics)
        
        # Step 2: Get attendance prediction
        prediction = AnalyticsService.get_attendance_prediction(self.class_id)
        self.assertIn('predicted_rate', prediction)
        self.assertIn('trend', prediction)
        self.assertIn('confidence', prediction)
        
        # Step 3: Get at-risk students
        at_risk = AnalyticsService.get_at_risk_students(self.class_id, threshold=75.0)
        # Some students should be at risk based on our test data
        self.assertIsInstance(at_risk, list)
        
        # Step 4: Get recommendations
        recommendations = AnalyticsService.get_smart_recommendations(self.class_id)
        self.assertGreater(len(recommendations), 0)
        
        # Step 5: Get trend analysis
        trend = AnalyticsService.get_trend_analysis(self.class_id)
        self.assertIn('trend', trend)
        self.assertIn('insight', trend)
        
        # Step 6: Export analytics report
        report = AnalyticsService.export_analytics_report(self.class_id)
        self.assertIn('class_name', report)
        self.assertIn('summary', report)
        self.assertIn('recommendations', report)


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestUserRegistrationLoginFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestClassManagementFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestAttendanceWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyticsWorkflow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)







