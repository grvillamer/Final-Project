"""
SpottEd Registration Page - CSPC Classroom Management System
Centered and Responsive Layout
"""
import flet as ft
from database import db
from utils.helpers import validate_email


def RegisterPage(page: ft.Page, on_register=None, on_back=None):
    """Registration page - Centered and Responsive"""
    
    # Form state
    first_name_field = ft.Ref[ft.TextField]()
    last_name_field = ft.Ref[ft.TextField]()
    role_dropdown = ft.Ref[ft.Dropdown]()
    email_field = ft.Ref[ft.TextField]()
    student_id_field = ft.Ref[ft.TextField]()
    course_dropdown = ft.Ref[ft.Dropdown]()
    year_dropdown = ft.Ref[ft.Dropdown]()
    password_field = ft.Ref[ft.TextField]()
    confirm_password_field = ft.Ref[ft.TextField]()
    terms_checkbox = ft.Ref[ft.Checkbox]()
    error_text = ft.Ref[ft.Text]()
    register_btn = ft.Ref[ft.ElevatedButton]()
    course_year_section = ft.Ref[ft.Container]()
    student_id_section = ft.Ref[ft.Container]()
    
    def show_error(message: str):
        error_text.current.value = message
        error_text.current.visible = True
        page.update()
    
    def hide_error():
        error_text.current.visible = False
        page.update()
    
    def on_role_change(e):
        is_student = role_dropdown.current.value == "student"
        course_year_section.current.visible = is_student
        student_id_section.current.visible = is_student
        page.update()
    
    def handle_register(e):
        hide_error()
        
        first_name = first_name_field.current.value.strip()
        last_name = last_name_field.current.value.strip()
        role = role_dropdown.current.value or "student"
        email = email_field.current.value.strip()
        course = course_dropdown.current.value if role == "student" else None
        year = year_dropdown.current.value if role == "student" else None
        password = password_field.current.value
        confirm_password = confirm_password_field.current.value
        agreed = terms_checkbox.current.value
        
        # For students, get Student ID; for instructors, generate Employee ID from email
        if role == "student":
            student_id = student_id_field.current.value.strip()
        else:
            # Generate unique Employee ID for instructors using email prefix + timestamp
            import time
            email_prefix = email.split('@')[0] if '@' in email else email
            employee_id = f"FAC-{email_prefix[:8].upper()}"
            student_id = employee_id
        
        if not first_name:
            show_error("Please enter your first name")
            return
        if not last_name:
            show_error("Please enter your last name")
            return
        if not email:
            show_error("Please enter your CSPC email")
            return
        if not validate_email(email):
            show_error("Please enter a valid email address")
            return
        if role == "student":
            if not student_id:
                show_error("Please enter your Student ID")
                return
            if len(student_id) < 4:
                show_error("Invalid Student ID format")
                return
        if role == "student":
            if not course:
                show_error("Please select your course")
                return
            if not year:
                show_error("Please select your year level")
                return
        if not password:
            show_error("Please create a password")
            return
        if len(password) < 8:
            show_error("Password must be at least 8 characters")
            return
        if not any(c.isdigit() for c in password):
            show_error("Password must contain at least one number")
            return
        if password != confirm_password:
            show_error("Passwords do not match")
            return
        if not agreed:
            show_error("Please agree to the Terms of Service and Privacy Policy")
            return
        
        # Check if email already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            show_error("This email is already registered. Please sign in instead.")
            return
        
        register_btn.current.disabled = True
        register_btn.current.content.controls[1].value = "Creating Account..."
        page.update()
        
        user_id = db.create_user(
            student_id=student_id, email=email, password=password,
            first_name=first_name, last_name=last_name, role=role
        )
        
        if user_id:
            if role == "student" and course and year:
                db.set_setting(user_id, 'course', course)
                db.set_setting(user_id, 'year', year)
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Account created successfully! Welcome to Smart Classroom."),
                bgcolor="#4CAF50",
            )
            page.snack_bar.open = True
            page.update()
            
            if on_register:
                user = db.get_user(user_id)
                on_register(user)
        else:
            if role == "student":
                show_error("Student ID or email already registered")
            else:
                show_error("Email already registered. Please sign in instead.")
            register_btn.current.disabled = False
            register_btn.current.content.controls[1].value = "Create Account"
            page.update()
    
    def handle_back(e):
        if on_back:
            on_back()
    
    # Centered content with max width
    content = ft.Container(
        content=ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="#ffffff", on_click=handle_back),
                    ft.Column([
                        ft.Text("Create Account", size=24, weight=ft.FontWeight.W_700, color="#ffffff"),
                        ft.Text("Join CSPC Classroom Management", size=14, color="#8b95a5"),
                    ], spacing=2),
                ], spacing=8),
                margin=ft.margin.only(bottom=20),
            ),
            
            # CSPC Logo Card
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text("CS", size=36, weight=ft.FontWeight.W_800, color="#ffffff"),
                        width=80, height=80, bgcolor="#4CAF50", border_radius=18,
                        alignment=ft.alignment.center,
                    ),
                    ft.Text("CSPC", size=26, weight=ft.FontWeight.W_800, color="#4CAF50"),
                    ft.Text("Camarines Sur Polytechnic Colleges", size=13, color="#8b95a5"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                bgcolor="#1a2332", padding=24, border_radius=16, width=float("inf"),
            ),
            
            ft.Container(height=16),
            
            # Error message
            ft.Text("", ref=error_text, size=13, color="#F44336", visible=False,
                    text_align=ft.TextAlign.CENTER),
            
            # Registration form
            ft.Container(
                content=ft.Column([
                    # Personal Information
                    ft.Text("Personal Information", size=14, weight=ft.FontWeight.W_600, color="#ffffff"),
                    ft.Container(height=10),
                    ft.Row([
                        ft.TextField(
                            ref=first_name_field, hint_text="First Name",
                            prefix_icon=ft.Icons.PERSON_OUTLINE, border_color="#2d3a4d",
                            focused_border_color="#4CAF50", hint_style=ft.TextStyle(color="#5a6474"),
                            text_style=ft.TextStyle(color="#ffffff"), cursor_color="#4CAF50",
                            border_radius=8, expand=True,
                        ),
                        ft.TextField(
                            ref=last_name_field, hint_text="Last Name",
                            prefix_icon=ft.Icons.PERSON_OUTLINE, border_color="#2d3a4d",
                            focused_border_color="#4CAF50", hint_style=ft.TextStyle(color="#5a6474"),
                            text_style=ft.TextStyle(color="#ffffff"), cursor_color="#4CAF50",
                            border_radius=8, expand=True,
                        ),
                    ], spacing=12),
                    
                    ft.Container(height=16),
                    
                    # Account Type
                    ft.Text("Account Type", size=14, weight=ft.FontWeight.W_600, color="#ffffff"),
                    ft.Container(height=8),
                    ft.Dropdown(
                        ref=role_dropdown, value="student",
                        options=[
                            ft.dropdown.Option("student", "Student"),
                            ft.dropdown.Option("instructor", "Faculty/Instructor"),
                        ],
                        border_color="#2d3a4d", focused_border_color="#4CAF50",
                        text_style=ft.TextStyle(color="#ffffff"), border_radius=8,
                        on_change=on_role_change,
                    ),
                    
                    ft.Container(height=12),
                    
                    # Email
                    ft.TextField(
                        ref=email_field, hint_text="name@my.cspc.edu.ph",
                        prefix_icon=ft.Icons.MAIL_OUTLINE, border_color="#2d3a4d",
                        focused_border_color="#4CAF50", hint_style=ft.TextStyle(color="#5a6474"),
                        text_style=ft.TextStyle(color="#ffffff"), cursor_color="#4CAF50", border_radius=8,
                    ),
                    
                    ft.Container(height=12),
                    
                    # Student ID (Students only)
                    ft.Container(
                        ref=student_id_section,
                        content=ft.Column([
                            ft.TextField(
                                ref=student_id_field, hint_text="Student ID (e.g., 231003956)",
                                prefix_icon=ft.Icons.BADGE_OUTLINED, border_color="#2d3a4d",
                                focused_border_color="#4CAF50", hint_style=ft.TextStyle(color="#5a6474"),
                                text_style=ft.TextStyle(color="#ffffff"), cursor_color="#4CAF50", border_radius=8,
                            ),
                        ]),
                        visible=True,
                    ),
                    
                    # Course and Year (Students only)
                    ft.Container(
                        ref=course_year_section,
                        content=ft.Column([
                            ft.Container(height=12),
                            ft.Row([
                                ft.Dropdown(
                                    ref=course_dropdown, hint_text="Course",
                                    options=[
                                        ft.dropdown.Option("BSCS", "BS Computer Science"),
                                        ft.dropdown.Option("BSIT", "BS Information Technology"),
                                        ft.dropdown.Option("BSIS", "BS Information System"),
                                        ft.dropdown.Option("BSLIS", "BS Library & Info System"),
                                    ],
                                    border_color="#2d3a4d", focused_border_color="#4CAF50",
                                    hint_style=ft.TextStyle(color="#5a6474"),
                                    text_style=ft.TextStyle(color="#ffffff"), border_radius=8, expand=True,
                                ),
                                ft.Dropdown(
                                    ref=year_dropdown, hint_text="Year",
                                    options=[
                                        ft.dropdown.Option("1", "1st Year"),
                                        ft.dropdown.Option("2", "2nd Year"),
                                        ft.dropdown.Option("3", "3rd Year"),
                                        ft.dropdown.Option("4", "4th Year"),
                                    ],
                                    border_color="#2d3a4d", focused_border_color="#4CAF50",
                                    hint_style=ft.TextStyle(color="#5a6474"),
                                    text_style=ft.TextStyle(color="#ffffff"), border_radius=8, width=120,
                                ),
                            ], spacing=12),
                        ]),
                        visible=True,
                    ),
                    
                    ft.Container(height=16),
                    
                    # Security
                    ft.Text("Security", size=14, weight=ft.FontWeight.W_600, color="#ffffff"),
                    ft.Container(height=8),
                    ft.TextField(
                        ref=password_field, hint_text="Password (min. 8 characters)",
                        prefix_icon=ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True,
                        border_color="#2d3a4d", focused_border_color="#4CAF50",
                        hint_style=ft.TextStyle(color="#5a6474"), text_style=ft.TextStyle(color="#ffffff"),
                        cursor_color="#4CAF50", border_radius=8,
                    ),
                    ft.Container(height=12),
                    ft.TextField(
                        ref=confirm_password_field, hint_text="Confirm Password",
                        prefix_icon=ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True,
                        border_color="#2d3a4d", focused_border_color="#4CAF50",
                        hint_style=ft.TextStyle(color="#5a6474"), text_style=ft.TextStyle(color="#ffffff"),
                        cursor_color="#4CAF50", border_radius=8, on_submit=handle_register,
                    ),
                    
                    ft.Container(height=12),
                    
                    # Terms checkbox
                    ft.Row([
                        ft.Checkbox(
                            ref=terms_checkbox, value=False, check_color="#ffffff",
                            fill_color={ft.ControlState.SELECTED: "#4CAF50",
                                        ft.ControlState.DEFAULT: "#2d3a4d"}, scale=0.9,
                        ),
                        ft.Text("I agree to the ", size=12, color="#8b95a5"),
                        ft.Text("Terms of Service", size=12, color="#4CAF50"),
                        ft.Text(" and ", size=12, color="#8b95a5"),
                        ft.Text("Privacy Policy", size=12, color="#4CAF50"),
                    ], spacing=0, wrap=True),
                    
                    ft.Container(height=8),
                    
                    ft.Text("By creating an account, you confirm that you are a current CSPC student, faculty, or staff member.",
                            size=11, color="#5a6474", text_align=ft.TextAlign.CENTER),
                ], spacing=0),
                bgcolor="#1a2332", padding=20, border_radius=12, width=float("inf"),
            ),
            
            ft.Container(height=20),
            
            # Register button
            ft.ElevatedButton(
                ref=register_btn,
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=20),
                    ft.Text("Create Account", size=16, weight=ft.FontWeight.W_600),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                bgcolor="#4CAF50", color="#ffffff", width=float("inf"), height=52,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                on_click=handle_register,
            ),
            
            ft.Container(height=16),
            
            # Login link
            ft.Row([
                ft.Text("Already have an account?", size=14, color="#8b95a5"),
                ft.TextButton(content=ft.Text("Sign In", size=14, weight=ft.FontWeight.W_600,
                                               color="#4CAF50"), on_click=handle_back),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
            
            ft.Container(height=20),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
        width=400,  # Max width for responsiveness
        padding=ft.padding.symmetric(horizontal=20),
    )
    
    # Center everything
    return ft.Container(
        content=ft.Row(
            controls=[content],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor="#0d1520",
        expand=True,
        padding=ft.padding.symmetric(vertical=16),
    )
