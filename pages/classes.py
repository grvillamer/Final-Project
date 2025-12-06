"""
SpottEd Classes Pages
"""
import flet as ft
from database import db
from components.cards import ClassCard, StudentCard
from utils.helpers import generate_class_code, get_initials


def ClassesPage(page: ft.Page, user: dict, on_navigate=None):
    """Classes list page"""
    
    is_instructor = user.get('role') == 'instructor'
    classes_list = ft.Ref[ft.Column]()
    join_code_field = ft.Ref[ft.TextField]()
    
    def load_classes():
        if is_instructor:
            return db.get_classes_by_instructor(user['id'])
        else:
            return db.get_enrolled_classes(user['id'])
    
    def refresh_list():
        classes = load_classes()
        classes_list.current.controls = [
            ClassCard(
                class_data=cls,
                on_click=lambda c: on_navigate('class_detail', c) if on_navigate else None,
                on_edit=lambda c: on_navigate('edit_class', c) if on_navigate else None,
                on_delete=handle_delete_class,
            ) if is_instructor else ClassCard(
                class_data=cls,
                on_click=lambda c: on_navigate('class_detail', c) if on_navigate else None,
            )
            for cls in classes
        ]
        page.update()
    
    def handle_delete_class(cls):
        def confirm_delete(e):
            db.delete_class(cls['id'])
            dialog.open = False
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Class deleted"),
                bgcolor="#F44336",
            )
            page.snack_bar.open = True
            refresh_list()
            page.update()
        
        def cancel_delete(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Delete Class?", color="#ffffff"),
            content=ft.Text(
                f"Are you sure you want to delete {cls['name']}? This action cannot be undone.",
                color="#8b95a5",
            ),
            bgcolor="#1a2332",
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.TextButton("Delete", on_click=confirm_delete, style=ft.ButtonStyle(color="#F44336")),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def handle_join_class(e):
        code = join_code_field.current.value.strip().upper()
        if not code:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please enter a class code"),
                bgcolor="#F44336",
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Find class by code
        cursor = db.conn.cursor()
        cursor.execute('SELECT * FROM classes WHERE class_code = ?', (code,))
        cls = cursor.fetchone()
        
        if not cls:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Class not found"),
                bgcolor="#F44336",
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Enroll student
        success = db.enroll_student(cls['id'], user['id'])
        if success:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Successfully joined class!"),
                bgcolor="#4CAF50",
            )
            join_code_field.current.value = ""
            refresh_list()
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Already enrolled in this class"),
                bgcolor="#FF9800",
            )
        page.snack_bar.open = True
        page.update()
    
    classes = load_classes()
    
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                "My Classes" if is_instructor else "My Classes",
                                size=24,
                                weight=ft.FontWeight.W_700,
                                color="#ffffff",
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                icon_color="#4CAF50",
                                on_click=lambda e: on_navigate('create_class') if on_navigate else None,
                            ) if is_instructor else ft.Container(),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    margin=ft.margin.only(bottom=16),
                ),
                
                # Join class section (for students)
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.TextField(
                                ref=join_code_field,
                                hint_text="Enter class code",
                                border_color="#2d3a4d",
                                focused_border_color="#4CAF50",
                                hint_style=ft.TextStyle(color="#8b95a5"),
                                text_style=ft.TextStyle(color="#ffffff"),
                                cursor_color="#4CAF50",
                                border_radius=10,
                                expand=True,
                                capitalization=ft.TextCapitalization.CHARACTERS,
                            ),
                            ft.ElevatedButton(
                                content=ft.Text("Join"),
                                bgcolor="#4CAF50",
                                color="#ffffff",
                                height=48,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                                on_click=handle_join_class,
                            ),
                        ],
                        spacing=12,
                    ),
                    margin=ft.margin.only(bottom=20),
                ) if not is_instructor else ft.Container(),
                
                # Classes list
                ft.Column(
                    ref=classes_list,
                    controls=[
                        ClassCard(
                            class_data=cls,
                            on_click=lambda c: on_navigate('class_detail', c) if on_navigate else None,
                            on_edit=lambda c: on_navigate('edit_class', c) if on_navigate else None,
                            on_delete=handle_delete_class,
                        ) if is_instructor else ClassCard(
                            class_data=cls,
                            on_click=lambda c: on_navigate('class_detail', c) if on_navigate else None,
                        )
                        for cls in classes
                    ] if classes else [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.SCHOOL_OUTLINED, size=64, color="#8b95a5"),
                                    ft.Text(
                                        "No classes yet",
                                        size=16,
                                        color="#8b95a5",
                                    ),
                                    ft.Text(
                                        "Create your first class" if is_instructor else "Join a class using the code above",
                                        size=13,
                                        color="#8b95a5",
                                    ),
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


def CreateClassPage(page: ft.Page, user: dict, on_save=None, on_back=None, edit_class=None):
    """Create or edit class page"""
    
    is_edit = edit_class is not None
    
    name_field = ft.Ref[ft.TextField]()
    description_field = ft.Ref[ft.TextField]()
    schedule_field = ft.Ref[ft.TextField]()
    room_field = ft.Ref[ft.TextField]()
    code_text = ft.Ref[ft.Text]()
    save_btn = ft.Ref[ft.ElevatedButton]()
    
    class_code = edit_class.get('class_code', '') if is_edit else generate_class_code()
    
    def handle_save(e):
        name = name_field.current.value.strip()
        description = description_field.current.value.strip()
        schedule = schedule_field.current.value.strip()
        room = room_field.current.value.strip()
        
        if not name:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please enter a class name"),
                bgcolor="#F44336",
            )
            page.snack_bar.open = True
            page.update()
            return
        
        save_btn.current.disabled = True
        save_btn.current.content.value = "Saving..."
        page.update()
        
        if is_edit:
            success = db.update_class(
                edit_class['id'],
                name=name,
                description=description,
                schedule=schedule,
                room=room,
            )
        else:
            class_id = db.create_class(
                class_code=class_code,
                name=name,
                instructor_id=user['id'],
                description=description,
                schedule=schedule,
                room=room,
            )
            success = class_id is not None
        
        if success:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Class saved successfully!"),
                bgcolor="#4CAF50",
            )
            page.snack_bar.open = True
            page.update()
            
            if on_save:
                on_save()
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Failed to save class"),
                bgcolor="#F44336",
            )
            page.snack_bar.open = True
            save_btn.current.disabled = False
            save_btn.current.content.value = "Save Class"
            page.update()
    
    def handle_back(e):
        if on_back:
            on_back()
    
    def copy_code(e):
        page.set_clipboard(class_code)
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Class code copied!"),
            bgcolor="#4CAF50",
        )
        page.snack_bar.open = True
        page.update()
    
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
                            ft.Text(
                                "Edit Class" if is_edit else "Create Class",
                                size=20,
                                weight=ft.FontWeight.W_600,
                                color="#ffffff",
                            ),
                        ],
                        spacing=8,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Class code display
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Class Code",
                                        size=12,
                                        color="#8b95a5",
                                    ),
                                    ft.Text(
                                        class_code,
                                        ref=code_text,
                                        size=28,
                                        weight=ft.FontWeight.W_700,
                                        color="#4CAF50",
                                        selectable=True,
                                    ),
                                ],
                                spacing=4,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.COPY,
                                icon_color="#4CAF50",
                                tooltip="Copy code",
                                on_click=copy_code,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor="#1a2332",
                    padding=16,
                    border_radius=12,
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Form
                ft.TextField(
                    ref=name_field,
                    label="Class Name *",
                    value=edit_class.get('name', '') if is_edit else '',
                    border_color="#2d3a4d",
                    focused_border_color="#4CAF50",
                    label_style=ft.TextStyle(color="#8b95a5"),
                    text_style=ft.TextStyle(color="#ffffff"),
                    cursor_color="#4CAF50",
                    border_radius=10,
                ),
                
                ft.TextField(
                    ref=description_field,
                    label="Description",
                    value=edit_class.get('description', '') if is_edit else '',
                    multiline=True,
                    min_lines=2,
                    max_lines=4,
                    border_color="#2d3a4d",
                    focused_border_color="#4CAF50",
                    label_style=ft.TextStyle(color="#8b95a5"),
                    text_style=ft.TextStyle(color="#ffffff"),
                    cursor_color="#4CAF50",
                    border_radius=10,
                ),
                
                ft.TextField(
                    ref=schedule_field,
                    label="Schedule",
                    value=edit_class.get('schedule', '') if is_edit else '',
                    hint_text="e.g., MWF 9:00 AM - 10:30 AM",
                    border_color="#2d3a4d",
                    focused_border_color="#4CAF50",
                    label_style=ft.TextStyle(color="#8b95a5"),
                    hint_style=ft.TextStyle(color="#5a6474"),
                    text_style=ft.TextStyle(color="#ffffff"),
                    cursor_color="#4CAF50",
                    border_radius=10,
                ),
                
                ft.TextField(
                    ref=room_field,
                    label="Room",
                    value=edit_class.get('room', '') if is_edit else '',
                    hint_text="e.g., Room 301",
                    border_color="#2d3a4d",
                    focused_border_color="#4CAF50",
                    label_style=ft.TextStyle(color="#8b95a5"),
                    hint_style=ft.TextStyle(color="#5a6474"),
                    text_style=ft.TextStyle(color="#ffffff"),
                    cursor_color="#4CAF50",
                    border_radius=10,
                ),
                
                # Save button
                ft.Container(
                    content=ft.ElevatedButton(
                        ref=save_btn,
                        content=ft.Text(
                            "Save Class",
                            size=16,
                            weight=ft.FontWeight.W_600,
                        ),
                        bgcolor="#4CAF50",
                        color="#ffffff",
                        width=float("inf"),
                        height=50,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=handle_save,
                    ),
                    margin=ft.margin.only(top=20),
                ),
            ],
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor="#0d1520",
        expand=True,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
    )


def ClassDetailPage(page: ft.Page, user: dict, class_data: dict, on_navigate=None, on_back=None):
    """Class detail page with students and attendance"""
    
    is_instructor = user.get('role') == 'instructor'
    students_list = ft.Ref[ft.Column]()
    
    def load_students():
        return db.get_class_students(class_data['id'])
    
    def refresh_students():
        students = load_students()
        students_list.current.controls = [
            StudentCard(student_data=s)
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
        ]
        page.update()
    
    students = load_students()
    sessions = db.get_class_sessions(class_data['id'])
    
    def handle_back(e):
        if on_back:
            on_back()
    
    def handle_take_attendance(e):
        if on_navigate:
            on_navigate('take_attendance', class_data)
    
    def copy_code(e):
        page.set_clipboard(class_data.get('class_code', ''))
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Class code copied!"),
            bgcolor="#4CAF50",
        )
        page.snack_bar.open = True
        page.update()
    
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
                            ft.Text(
                                class_data.get('name', 'Class'),
                                size=20,
                                weight=ft.FontWeight.W_600,
                                color="#ffffff",
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                icon_color="#8b95a5",
                                on_click=lambda e: on_navigate('edit_class', class_data) if on_navigate else None,
                            ) if is_instructor else ft.Container(),
                        ],
                    ),
                    margin=ft.margin.only(bottom=16),
                ),
                
                # Class info card
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            class_data.get('class_code', 'N/A'),
                                            size=18,
                                            weight=ft.FontWeight.W_700,
                                            color="#4CAF50",
                                        ),
                                        bgcolor="#1a3d2e",
                                        padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                        border_radius=8,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.COPY,
                                        icon_size=18,
                                        icon_color="#8b95a5",
                                        tooltip="Copy code",
                                        on_click=copy_code,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                class_data.get('description', 'No description'),
                                size=13,
                                color="#8b95a5",
                            ) if class_data.get('description') else ft.Container(),
                            ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.SCHEDULE, size=14, color="#8b95a5"),
                                            ft.Text(
                                                class_data.get('schedule', 'No schedule'),
                                                size=12,
                                                color="#8b95a5",
                                            ),
                                        ],
                                        spacing=6,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=14, color="#8b95a5"),
                                            ft.Text(
                                                class_data.get('room', 'No room'),
                                                size=12,
                                                color="#8b95a5",
                                            ),
                                        ],
                                        spacing=6,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor="#1a2332",
                    padding=16,
                    border_radius=12,
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Take attendance button (instructor only)
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.HOW_TO_REG, size=20),
                                ft.Text("Take Attendance", size=15, weight=ft.FontWeight.W_600),
                            ],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        bgcolor="#4CAF50",
                        color="#ffffff",
                        width=float("inf"),
                        height=50,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=handle_take_attendance,
                    ),
                    margin=ft.margin.only(bottom=20),
                ) if is_instructor else ft.Container(),
                
                # Stats
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(str(len(students)), size=24, weight=ft.FontWeight.W_700, color="#4CAF50"),
                                    ft.Text("Students", size=12, color="#8b95a5"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            bgcolor="#1a2332",
                            padding=16,
                            border_radius=10,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(str(len(sessions)), size=24, weight=ft.FontWeight.W_700, color="#2196F3"),
                                    ft.Text("Sessions", size=12, color="#8b95a5"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            bgcolor="#1a2332",
                            padding=16,
                            border_radius=10,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
                
                # Students section
                ft.Container(
                    content=ft.Text(
                        "Enrolled Students",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color="#ffffff",
                    ),
                    margin=ft.margin.only(top=24, bottom=12),
                ),
                
                ft.Column(
                    ref=students_list,
                    controls=[
                        StudentCard(student_data=s)
                        for s in students
                    ] if students else [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.PEOPLE_OUTLINED, size=48, color="#8b95a5"),
                                    ft.Text("No students enrolled", size=14, color="#8b95a5"),
                                    ft.Text("Share the class code to invite students", size=12, color="#5a6474"),
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








