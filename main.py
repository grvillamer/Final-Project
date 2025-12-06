"""
Smart Classroom - Access Control System
Main Application Entry Point

A secure cross-platform classroom management application built with Flet (Python + Flutter).
Implements RBAC, audit logging, and security controls per Information Assurance requirements.

Runs on Desktop, Web, and Mobile platforms.
"""
import flet as ft
from datetime import datetime, timedelta
from database import db
from utils.theme import get_theme
from config import config
from core.audit import audit_logger

# Import pages
from pages.splash import SplashPage
from pages.login import LoginPage
from pages.register import RegisterPage
from pages.forgot_password import ForgotPasswordPage
from pages.home import HomePage
from pages.activity import ActivityPage
from pages.schedule import SchedulePage
from pages.classes import ClassesPage, CreateClassPage, ClassDetailPage
from pages.attendance import AttendancePage, AttendanceSessionPage
from pages.analytics import AnalyticsPage
from pages.settings import SettingsPage, ProfilePage
from pages.admin import AdminPage
from pages.audit_logs import AuditLogsPage


def main(page: ft.Page):
    """Main application entry point"""
    
    # App configuration
    page.title = "Smart Classroom Availability and Locator App for CCS"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0d1520"
    page.padding = 0
    
    # Detect platform and configure accordingly
    is_web = page.web
    is_mobile = page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]
    
    # Responsive sizing based on platform
    if not is_web and not is_mobile:
        # Desktop - set window size
        page.window.width = 420
        page.window.height = 850
        page.window.min_width = 320
        page.window.min_height = 600
        page.window.resizable = True
    
    # Web and mobile will automatically adapt to screen size
    
    # App state
    current_user = {"user": None}
    current_nav_index = {"index": 0}
    navigation_stack = []
    
    # ==================== THEME ====================
    
    def apply_theme():
        """Apply theme based on user preference"""
        c = get_theme(page)
        page.bgcolor = c["bg_primary"]
    
    def load_user_theme(user_id: int):
        """Load and apply user's saved theme preference"""
        if user_id:
            theme = db.get_setting(user_id, 'theme', 'dark')
            if theme == 'light':
                page.theme_mode = ft.ThemeMode.LIGHT
                page.bgcolor = "#f5f7fa"
            else:
                page.theme_mode = ft.ThemeMode.DARK
                page.bgcolor = "#0d1520"
    
    # ==================== NAVIGATION ====================
    
    def create_bottom_nav(selected_index: int = 0) -> ft.NavigationBar:
        """Create bottom navigation bar"""
        c = get_theme(page)
        return ft.NavigationBar(
            selected_index=selected_index,
            on_change=handle_nav_change,
            bgcolor=c["nav_bg"],
            indicator_color=c["accent_bg"],
            surface_tint_color="transparent",
            height=65,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Home",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.HISTORY_OUTLINED,
                    selected_icon=ft.Icons.HISTORY,
                    label="Activity",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                    selected_icon=ft.Icons.CALENDAR_MONTH,
                    label="Schedule",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings",
                ),
            ],
        )
    
    def handle_nav_change(e):
        """Handle bottom navigation changes"""
        index = e.control.selected_index
        current_nav_index["index"] = index
        navigation_stack.clear()
        
        if index == 0:
            navigate_to('home')
        elif index == 1:
            navigate_to('activity')
        elif index == 2:
            navigate_to('schedule')
        elif index == 3:
            navigate_to('settings')
    
    def navigate_to(route: str, data=None):
        """Navigate to a specific route"""
        user = current_user["user"]
        
        content = None
        show_nav = True
        
        if route == 'splash':
            show_nav = False
            content = SplashPage(page, on_complete=lambda: navigate_to('login'))
        
        elif route == 'login':
            show_nav = False
            content = LoginPage(
                page,
                on_login=handle_login,
                on_register=lambda: navigate_to('register'),
                on_forgot_password=lambda: navigate_to('forgot_password'),
            )
        
        elif route == 'register':
            show_nav = False
            content = RegisterPage(
                page,
                on_register=handle_login,
                on_back=lambda: navigate_to('login'),
            )
        
        elif route == 'forgot_password':
            show_nav = False
            content = ForgotPasswordPage(
                page,
                on_back=lambda: navigate_to('login'),
            )
        
        elif route == 'home':
            content = HomePage(
                page,
                user=user,
                on_navigate=handle_home_navigate,
            )
        
        elif route == 'activity':
            content = ActivityPage(
                page,
                user=user,
                on_navigate=handle_home_navigate,
            )
        
        elif route == 'schedule':
            content = SchedulePage(
                page,
                user=user,
                on_navigate=handle_home_navigate,
            )
        
        elif route == 'classes':
            content = ClassesPage(
                page,
                user=user,
                on_navigate=handle_classes_navigate,
            )
        
        elif route == 'create_class':
            show_nav = False
            content = CreateClassPage(
                page,
                user=user,
                on_save=lambda: navigate_to('classes'),
                on_back=lambda: navigate_back(),
            )
        
        elif route == 'edit_class':
            show_nav = False
            content = CreateClassPage(
                page,
                user=user,
                edit_class=data,
                on_save=lambda: navigate_to('classes'),
                on_back=lambda: navigate_back(),
            )
        
        elif route == 'class_detail':
            show_nav = False
            content = ClassDetailPage(
                page,
                user=user,
                class_data=data,
                on_navigate=handle_class_detail_navigate,
                on_back=lambda: navigate_back(),
            )
        
        elif route == 'attendance':
            content = AttendancePage(
                page,
                user=user,
                on_navigate=handle_attendance_navigate,
            )
        
        elif route == 'take_attendance':
            show_nav = False
            content = AttendanceSessionPage(
                page,
                user=user,
                class_data=data,
                on_back=lambda: navigate_back(),
            )
        
        elif route == 'analytics':
            content = AnalyticsPage(
                page,
                user=user,
                on_navigate=handle_analytics_navigate,
            )
        
        elif route == 'settings':
            content = SettingsPage(
                page,
                user=user,
                on_navigate=handle_settings_navigate,
                on_logout=handle_logout,
            )
        
        elif route == 'profile':
            show_nav = False
            content = ProfilePage(
                page,
                user=user,
                on_back=lambda: navigate_back(),
            )
        
        elif route == 'admin':
            show_nav = False
            content = AdminPage(
                page,
                user=user,
                on_navigate=handle_admin_navigate,
            )
        
        elif route == 'audit_logs':
            show_nav = False
            content = AuditLogsPage(
                page,
                user=user,
                on_navigate=handle_admin_navigate,
            )
        
        # Build the page view
        page.controls.clear()
        
        if show_nav and user:
            page.controls.append(
                ft.Column(
                    controls=[
                        ft.Container(
                            content=content,
                            expand=True,
                        ),
                        create_bottom_nav(current_nav_index["index"]),
                    ],
                    expand=True,
                    spacing=0,
                )
            )
        else:
            page.controls.append(content)
        
        page.update()
    
    def navigate_back():
        """Navigate back to previous route"""
        if navigation_stack:
            prev = navigation_stack.pop()
            navigate_to(prev['route'], prev.get('data'))
        else:
            navigate_to('home')
    
    def push_navigation(route: str, data=None):
        """Push current route to stack and navigate"""
        # Store current route
        current_routes = ['home', 'classes', 'attendance', 'analytics', 'settings']
        current = current_routes[current_nav_index["index"]]
        navigation_stack.append({'route': current, 'data': None})
        navigate_to(route, data)
    
    # ==================== NAVIGATION HANDLERS ====================
    
    def handle_home_navigate(route: str, data=None):
        """Handle navigation from home page"""
        if route == 'classes':
            current_nav_index["index"] = 1
            navigate_to('classes')
        elif route == 'create_class':
            push_navigation('create_class')
        elif route == 'class_detail':
            push_navigation('class_detail', data)
        elif route == 'attendance':
            current_nav_index["index"] = 2
            navigate_to('attendance')
        elif route == 'scan':
            current_nav_index["index"] = 2
            navigate_to('attendance')
    
    def handle_classes_navigate(route: str, data=None):
        """Handle navigation from classes page"""
        if route == 'create_class':
            push_navigation('create_class')
        elif route == 'edit_class':
            push_navigation('edit_class', data)
        elif route == 'class_detail':
            push_navigation('class_detail', data)
    
    def handle_class_detail_navigate(route: str, data=None):
        """Handle navigation from class detail page"""
        if route == 'edit_class':
            navigation_stack.append({'route': 'class_detail', 'data': data})
            navigate_to('edit_class', data)
        elif route == 'take_attendance':
            navigation_stack.append({'route': 'class_detail', 'data': data})
            navigate_to('take_attendance', data)
    
    def handle_attendance_navigate(route: str, data=None):
        """Handle navigation from attendance page"""
        if route == 'take_attendance':
            push_navigation('take_attendance', data)
    
    def handle_analytics_navigate(route: str, data=None):
        """Handle navigation from analytics page"""
        pass
    
    def handle_settings_navigate(route: str, data=None):
        """Handle navigation from settings page"""
        if route == 'home':
            current_nav_index["index"] = 0
            apply_theme()
            navigate_to('home')
        elif route == 'settings':
            apply_theme()
            navigate_to('settings')
        elif route == 'profile':
            push_navigation('profile')
        elif route == 'change_password':
            push_navigation('change_password')
        elif route == 'admin':
            push_navigation('admin')
        elif route == 'audit_logs':
            push_navigation('audit_logs')
    
    def handle_admin_navigate(route: str, data=None):
        """Handle navigation from admin pages"""
        if route == 'home':
            current_nav_index["index"] = 0
            navigate_to('home')
        elif route == 'settings':
            current_nav_index["index"] = 3
            navigate_to('settings')
        elif route == 'admin':
            navigate_to('admin')
        elif route == 'audit_logs':
            navigate_to('audit_logs')
    
    # ==================== AUTH HANDLERS ====================
    
    def handle_login(user: dict):
        """Handle successful login"""
        current_user["user"] = user
        current_nav_index["index"] = 0
        navigation_stack.clear()
        # Load user's theme preference
        load_user_theme(user.get('id'))
        # Log successful login
        audit_logger.log_login_success(user.get('id'), user.get('student_id'))
        navigate_to('home')
    
    def handle_logout():
        """Handle logout"""
        user = current_user["user"]
        if user:
            audit_logger.log_logout(user.get('id'), user.get('student_id'))
        current_user["user"] = None
        current_nav_index["index"] = 0
        navigation_stack.clear()
        # Reset to dark theme
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#0d1520"
        navigate_to('login')
    
    # ==================== STARTUP ====================
    
    # Create sample data for demo
    def create_sample_data():
        """Create sample data for demonstration"""
        # Check if sample data already exists
        cursor = db.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users')
        if cursor.fetchone()['count'] > 0:
            return
        
        # Create sample instructor
        instructor_id = db.create_user(
            student_id="INST001",
            email="instructor@school.edu",
            password="password123",
            first_name="John",
            last_name="Smith",
            role="instructor"
        )
        
        # Create sample students
        students = [
            ("STU001", "alice@school.edu", "Alice", "Johnson"),
            ("STU002", "bob@school.edu", "Bob", "Williams"),
            ("STU003", "carol@school.edu", "Carol", "Brown"),
            ("STU004", "david@school.edu", "David", "Jones"),
            ("STU005", "emma@school.edu", "Emma", "Davis"),
            ("STU006", "frank@school.edu", "Frank", "Miller"),
            ("STU007", "grace@school.edu", "Grace", "Wilson"),
            ("STU008", "henry@school.edu", "Henry", "Moore"),
        ]
        
        student_ids = []
        for sid, email, first, last in students:
            user_id = db.create_user(
                student_id=sid,
                email=email,
                password="password123",
                first_name=first,
                last_name=last,
                role="student"
            )
            if user_id:
                student_ids.append(user_id)
        
        # Create sample classes
        if instructor_id:
            classes = [
                ("CS101", "Introduction to Programming", "MWF 9:00 AM - 10:30 AM", "Room 301"),
                ("CS201", "Data Structures", "TTH 2:00 PM - 3:30 PM", "Room 205"),
                ("CS301", "Database Systems", "MWF 1:00 PM - 2:30 PM", "Lab 101"),
            ]
            
            for code, name, schedule, room in classes:
                class_id = db.create_class(
                    class_code=code,
                    name=name,
                    instructor_id=instructor_id,
                    description=f"An introductory course in {name.lower()}",
                    schedule=schedule,
                    room=room,
                )
                
                # Enroll some students
                if class_id:
                    for i, student_id in enumerate(student_ids):
                        if i < 6:  # Enroll first 6 students in each class
                            db.enroll_student(class_id, student_id)
                    
                    # Create some attendance sessions
                    from datetime import datetime, timedelta
                    import random
                    
                    for days_ago in range(14, 0, -2):
                        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                        session_id = db.create_attendance_session(class_id, date)
                        
                        if session_id:
                            # Mark random attendance
                            for student_id in student_ids[:6]:
                                status = random.choices(
                                    ['present', 'late', 'absent'],
                                    weights=[0.7, 0.15, 0.15]
                                )[0]
                                db.mark_attendance(session_id, student_id, status)
    
    # Initialize sample data
    create_sample_data()
    
    # Start with splash screen
    navigate_to('splash')


# Run the app
if __name__ == "__main__":
    # The app automatically runs on the appropriate platform:
    # - Desktop: flet run main.py
    # - Web: flet run main.py --web (or flet run main.py -w)
    # - Android: flet run main.py --android
    # - iOS: flet run main.py --ios
    ft.app(
        target=main,
        assets_dir="assets",  # For static assets
    )



