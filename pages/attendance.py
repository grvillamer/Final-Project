"""
SpottEd Attendance Pages
"""
import flet as ft
from datetime import datetime
from database import db
from components.cards import StudentCard, AttendanceCard
from utils.helpers import generate_qr_code


def AttendancePage(page: ft.Page, user: dict, on_navigate=None):
    """Attendance management page"""
    
    is_instructor = user.get('role') == 'instructor'
    
    if is_instructor:
        return InstructorAttendancePage(page, user, on_navigate)
    else:
        return StudentAttendancePage(page, user, on_navigate)


def InstructorAttendancePage(page: ft.Page, user: dict, on_navigate=None):
    """Instructor attendance page - select class to take attendance"""
    
    classes = db.get_classes_by_instructor(user['id'])
    
    def handle_class_select(cls):
        if on_navigate:
            on_navigate('take_attendance', cls)
    
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Text(
                    "Take Attendance",
                    size=24,
                    weight=ft.FontWeight.W_700,
                    color="#ffffff",
                ),
                ft.Text(
                    "Select a class to take attendance",
                    size=14,
                    color="#8b95a5",
                ),
                
                ft.Container(height=20),
                
                # Classes list
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            cls.get('class_code', 'N/A'),
                                            size=14,
                                            weight=ft.FontWeight.W_700,
                                            color="#4CAF50",
                                        ),
                                        bgcolor="#1a3d2e",
                                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                        border_radius=8,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                cls.get('name', 'Unnamed'),
                                                size=16,
                                                weight=ft.FontWeight.W_500,
                                                color="#ffffff",
                                            ),
                                            ft.Text(
                                                f"{cls.get('student_count', 0)} students",
                                                size=12,
                                                color="#8b95a5",
                                            ),
                                        ],
                                        spacing=2,
                                        expand=True,
                                    ),
                                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color="#8b95a5"),
                                ],
                                spacing=12,
                            ),
                            bgcolor="#1a2332",
                            padding=16,
                            border_radius=12,
                            on_click=lambda e, c=cls: handle_class_select(c),
                            ink=True,
                        )
                        for cls in classes
                    ] if classes else [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.SCHOOL_OUTLINED, size=64, color="#8b95a5"),
                                    ft.Text("No classes yet", size=16, color="#8b95a5"),
                                    ft.Text("Create a class first", size=13, color="#5a6474"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            padding=60,
                            alignment=ft.alignment.center,
                        ),
                    ],
                    spacing=12,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor="#0d1520",
        expand=True,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
    )


def StudentAttendancePage(page: ft.Page, user: dict, on_navigate=None):
    """Student attendance page - scan QR or enter code"""
    
    code_field = ft.Ref[ft.TextField]()
    
    def handle_submit(e):
        code = code_field.current.value.strip()
        if not code:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please enter an attendance code"),
                bgcolor="#F44336",
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Find session by QR code
        session = db.get_session_by_qr(code)
        
        if not session:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Invalid or expired attendance code"),
                bgcolor="#F44336",
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Check if enrolled
        cls = db.get_class(session['class_id'])
        enrolled_classes = db.get_enrolled_classes(user['id'])
        is_enrolled = any(c['id'] == session['class_id'] for c in enrolled_classes)
        
        if not is_enrolled:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("You are not enrolled in this class"),
                bgcolor="#F44336",
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Mark attendance
        success = db.mark_attendance(session['id'], user['id'], 'present')
        
        if success:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Attendance marked for {cls['name']}!"),
                bgcolor="#4CAF50",
            )
            code_field.current.value = ""
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Already marked attendance"),
                bgcolor="#FF9800",
            )
        page.snack_bar.open = True
        page.update()
    
    # Get recent attendance
    history = db.get_student_attendance_history(user['id'])[:10]
    
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Text(
                    "Mark Attendance",
                    size=24,
                    weight=ft.FontWeight.W_700,
                    color="#ffffff",
                ),
                
                ft.Container(height=20),
                
                # QR Scanner placeholder
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.QR_CODE_SCANNER,
                                size=80,
                                color="#4CAF50",
                            ),
                            ft.Text(
                                "Scan QR Code",
                                size=16,
                                weight=ft.FontWeight.W_600,
                                color="#ffffff",
                            ),
                            ft.Text(
                                "Point your camera at the attendance QR code",
                                size=12,
                                color="#8b95a5",
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    bgcolor="#1a2332",
                    padding=40,
                    border_radius=12,
                    alignment=ft.alignment.center,
                ),
                
                # Or divider
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(height=1, bgcolor="#2d3a4d", expand=True),
                            ft.Text("or enter code manually", size=12, color="#8b95a5"),
                            ft.Container(height=1, bgcolor="#2d3a4d", expand=True),
                        ],
                        spacing=16,
                    ),
                    margin=ft.margin.symmetric(vertical=20),
                ),
                
                # Manual code entry
                ft.Row(
                    controls=[
                        ft.TextField(
                            ref=code_field,
                            hint_text="Enter attendance code",
                            border_color="#2d3a4d",
                            focused_border_color="#4CAF50",
                            hint_style=ft.TextStyle(color="#8b95a5"),
                            text_style=ft.TextStyle(color="#ffffff"),
                            cursor_color="#4CAF50",
                            border_radius=10,
                            expand=True,
                            on_submit=handle_submit,
                        ),
                        ft.ElevatedButton(
                            content=ft.Icon(ft.Icons.SEND, size=20),
                            bgcolor="#4CAF50",
                            color="#ffffff",
                            height=48,
                            width=48,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                            on_click=handle_submit,
                        ),
                    ],
                    spacing=12,
                ),
                
                # Recent attendance
                ft.Container(
                    content=ft.Text(
                        "Recent Attendance",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color="#ffffff",
                    ),
                    margin=ft.margin.only(top=30, bottom=12),
                ),
                
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                record.get('class_name', 'Unknown'),
                                                size=14,
                                                weight=ft.FontWeight.W_500,
                                                color="#ffffff",
                                            ),
                                            ft.Text(
                                                record.get('session_date', ''),
                                                size=11,
                                                color="#8b95a5",
                                            ),
                                        ],
                                        spacing=2,
                                        expand=True,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            record.get('status', 'absent').capitalize(),
                                            size=11,
                                            weight=ft.FontWeight.W_600,
                                            color="#ffffff",
                                        ),
                                        bgcolor="#4CAF50" if record.get('status') == 'present' else (
                                            "#FFC107" if record.get('status') == 'late' else "#F44336"
                                        ),
                                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                        border_radius=12,
                                    ),
                                ],
                            ),
                            bgcolor="#1a2332",
                            padding=12,
                            border_radius=10,
                        )
                        for record in history
                    ] if history else [
                        ft.Container(
                            content=ft.Text(
                                "No attendance history yet",
                                size=14,
                                color="#8b95a5",
                            ),
                            padding=20,
                            alignment=ft.alignment.center,
                        ),
                    ],
                    spacing=8,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor="#0d1520",
        expand=True,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
    )


def AttendanceSessionPage(page: ft.Page, user: dict, class_data: dict, on_back=None):
    """Take attendance for a class session"""
    
    students_list = ft.Ref[ft.Column]()
    qr_container = ft.Ref[ft.Container]()
    qr_code_text = ft.Ref[ft.Text]()
    
    # Create or get today's session
    today = datetime.now().strftime("%Y-%m-%d")
    sessions = db.get_class_sessions(class_data['id'])
    
    today_session = next(
        (s for s in sessions if s['session_date'] == today),
        None
    )
    
    if not today_session:
        qr_code = generate_qr_code()
        session_id = db.create_attendance_session(class_data['id'], today, qr_code)
        today_session = db.get_attendance_session(session_id)
    
    attendance_data = {}
    
    def load_attendance():
        records = db.get_session_attendance(today_session['id'])
        for record in records:
            attendance_data[record['id']] = record.get('status', 'absent')
        return records
    
    def handle_status_change(student, status):
        db.mark_attendance(today_session['id'], student['id'], status)
        attendance_data[student['id']] = status
        refresh_students()
    
    def refresh_students():
        students = load_attendance()
        students_list.current.controls = [
            StudentCard(
                student_data=s,
                status=attendance_data.get(s['id'], 'absent'),
                show_status_buttons=True,
                on_status_change=handle_status_change,
            )
            for s in students
        ] if students else [
            ft.Container(
                content=ft.Text("No students enrolled", color="#8b95a5"),
                padding=40,
                alignment=ft.alignment.center,
            ),
        ]
        page.update()
    
    students = load_attendance()
    
    def handle_back(e):
        if on_back:
            on_back()
    
    def copy_qr_code(e):
        page.set_clipboard(today_session.get('qr_code', ''))
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Attendance code copied!"),
            bgcolor="#4CAF50",
        )
        page.snack_bar.open = True
        page.update()
    
    def mark_all_present(e):
        students = db.get_class_students(class_data['id'])
        for student in students:
            db.mark_attendance(today_session['id'], student['id'], 'present')
            attendance_data[student['id']] = 'present'
        refresh_students()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("All students marked present"),
            bgcolor="#4CAF50",
        )
        page.snack_bar.open = True
        page.update()
    
    present_count = len([s for s in attendance_data.values() if s == 'present'])
    late_count = len([s for s in attendance_data.values() if s == 'late'])
    total_count = len(students)
    
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color="#ffffff",
                                on_click=handle_back,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        class_data.get('name', 'Class'),
                                        size=18,
                                        weight=ft.FontWeight.W_600,
                                        color="#ffffff",
                                    ),
                                    ft.Text(
                                        today,
                                        size=12,
                                        color="#8b95a5",
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                    ),
                    margin=ft.margin.only(bottom=16),
                ),
                
                # QR Code section
                ft.Container(
                    ref=qr_container,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Attendance Code",
                                size=12,
                                color="#8b95a5",
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        today_session.get('qr_code', 'N/A'),
                                        ref=qr_code_text,
                                        size=18,
                                        weight=ft.FontWeight.W_700,
                                        color="#4CAF50",
                                        selectable=True,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.COPY,
                                        icon_size=18,
                                        icon_color="#4CAF50",
                                        tooltip="Copy code",
                                        on_click=copy_qr_code,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Text(
                                "Share this code with students",
                                size=11,
                                color="#5a6474",
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    bgcolor="#1a2332",
                    padding=16,
                    border_radius=12,
                    margin=ft.margin.only(bottom=16),
                ),
                
                # Stats row
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        str(present_count),
                                        size=20,
                                        weight=ft.FontWeight.W_700,
                                        color="#4CAF50",
                                    ),
                                    ft.Text("Present", size=11, color="#8b95a5"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            bgcolor="#1a2332",
                            padding=12,
                            border_radius=8,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        str(late_count),
                                        size=20,
                                        weight=ft.FontWeight.W_700,
                                        color="#FFC107",
                                    ),
                                    ft.Text("Late", size=11, color="#8b95a5"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            bgcolor="#1a2332",
                            padding=12,
                            border_radius=8,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        str(total_count - present_count - late_count),
                                        size=20,
                                        weight=ft.FontWeight.W_700,
                                        color="#F44336",
                                    ),
                                    ft.Text("Absent", size=11, color="#8b95a5"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            bgcolor="#1a2332",
                            padding=12,
                            border_radius=8,
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
                
                # Quick action
                ft.Container(
                    content=ft.TextButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, size=18),
                                ft.Text("Mark All Present", size=13),
                            ],
                            spacing=6,
                        ),
                        style=ft.ButtonStyle(color="#4CAF50"),
                        on_click=mark_all_present,
                    ),
                    alignment=ft.alignment.center_right,
                    margin=ft.margin.only(top=8, bottom=4),
                ),
                
                # Students list
                ft.Text(
                    "Students",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color="#ffffff",
                ),
                
                ft.Column(
                    ref=students_list,
                    controls=[
                        StudentCard(
                            student_data=s,
                            status=attendance_data.get(s['id'], 'absent'),
                            show_status_buttons=True,
                            on_status_change=handle_status_change,
                        )
                        for s in students
                    ] if students else [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.PEOPLE_OUTLINED, size=48, color="#8b95a5"),
                                    ft.Text("No students enrolled", size=14, color="#8b95a5"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            padding=40,
                            alignment=ft.alignment.center,
                        ),
                    ],
                    spacing=10,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor="#0d1520",
        expand=True,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
    )








