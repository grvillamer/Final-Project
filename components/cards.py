"""
SpottEd Card Components
"""
import flet as ft
from utils.helpers import get_initials, get_status_color, get_attendance_status_color


def ClassCard(
    class_data: dict,
    on_click=None,
    on_edit=None,
    on_delete=None
) -> ft.Container:
    """Class card component"""
    
    student_count = class_data.get('student_count', 0)
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                class_data.get('class_code', 'N/A'),
                                size=14,
                                weight=ft.FontWeight.W_700,
                                color="#4CAF50",
                            ),
                            bgcolor="#1a3d2e",
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            border_radius=8,
                        ),
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=18,
                                    icon_color="#8b95a5",
                                    on_click=lambda e, c=class_data: on_edit(c) if on_edit else None,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINED,
                                    icon_size=18,
                                    icon_color="#F44336",
                                    on_click=lambda e, c=class_data: on_delete(c) if on_delete else None,
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    class_data.get('name', 'Unnamed Class'),
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color="#ffffff",
                ),
                ft.Text(
                    class_data.get('schedule', 'No schedule set'),
                    size=13,
                    color="#8b95a5",
                ),
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=14, color="#8b95a5"),
                                ft.Text(
                                    class_data.get('room', 'No room'),
                                    size=12,
                                    color="#8b95a5",
                                ),
                            ],
                            spacing=4,
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.PEOPLE_OUTLINED, size=14, color="#8b95a5"),
                                ft.Text(
                                    f"{student_count} students",
                                    size=12,
                                    color="#8b95a5",
                                ),
                            ],
                            spacing=4,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=8,
        ),
        bgcolor="#1a2332",
        padding=16,
        border_radius=12,
        on_click=lambda e, c=class_data: on_click(c) if on_click else None,
        ink=True,
    )


def StudentCard(
    student_data: dict,
    status: str = None,
    on_click=None,
    on_status_change=None,
    show_status_buttons: bool = False
) -> ft.Container:
    """Student card component"""
    
    initials = get_initials(
        student_data.get('first_name', ''),
        student_data.get('last_name', '')
    )
    
    full_name = f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}".strip()
    
    status_color = get_status_color(status) if status else "#9E9E9E"
    
    content_controls = [
        ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        initials,
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color="#ffffff",
                    ),
                    width=44,
                    height=44,
                    bgcolor="#2d3a4d",
                    border_radius=22,
                    alignment=ft.alignment.center,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            full_name or "Unknown Student",
                            size=15,
                            weight=ft.FontWeight.W_500,
                            color="#ffffff",
                        ),
                        ft.Text(
                            student_data.get('student_id', 'No ID'),
                            size=12,
                            color="#8b95a5",
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=12,
            expand=True,
        ),
    ]
    
    if show_status_buttons:
        content_controls.append(
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        content=ft.Text("Present", size=11),
                        bgcolor="#4CAF50" if status == "present" else "#2d3a4d",
                        color="#ffffff",
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            shape=ft.RoundedRectangleBorder(radius=6),
                        ),
                        on_click=lambda e, s=student_data: on_status_change(s, "present") if on_status_change else None,
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("Late", size=11),
                        bgcolor="#FFC107" if status == "late" else "#2d3a4d",
                        color="#ffffff" if status == "late" else "#8b95a5",
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            shape=ft.RoundedRectangleBorder(radius=6),
                        ),
                        on_click=lambda e, s=student_data: on_status_change(s, "late") if on_status_change else None,
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("Absent", size=11),
                        bgcolor="#F44336" if status == "absent" else "#2d3a4d",
                        color="#ffffff" if status == "absent" else "#8b95a5",
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            shape=ft.RoundedRectangleBorder(radius=6),
                        ),
                        on_click=lambda e, s=student_data: on_status_change(s, "absent") if on_status_change else None,
                    ),
                ],
                spacing=8,
                wrap=True,
            )
        )
    elif status:
        content_controls[0].controls.append(
            ft.Container(
                content=ft.Text(
                    status.capitalize(),
                    size=11,
                    weight=ft.FontWeight.W_600,
                    color="#ffffff" if status != "absent" else "#ffffff",
                ),
                bgcolor=status_color,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                border_radius=12,
            )
        )
    
    return ft.Container(
        content=ft.Column(
            controls=content_controls,
            spacing=12,
        ),
        bgcolor="#1a2332",
        padding=12,
        border_radius=10,
        on_click=lambda e, s=student_data: on_click(s) if on_click else None,
        ink=True if on_click else False,
    )


def AttendanceCard(
    session_data: dict,
    on_click=None
) -> ft.Container:
    """Attendance session card"""
    
    present = session_data.get('present_count', 0)
    total = session_data.get('total_students', 0)
    rate = (present / total * 100) if total > 0 else 0
    
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            session_data.get('session_date', 'Unknown Date'),
                            size=15,
                            weight=ft.FontWeight.W_500,
                            color="#ffffff",
                        ),
                        ft.Text(
                            f"{present}/{total} present",
                            size=12,
                            color="#8b95a5",
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Text(
                        f"{rate:.0f}%",
                        size=16,
                        weight=ft.FontWeight.W_700,
                        color=get_attendance_status_color(rate),
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=8,
                    bgcolor="#0d1520",
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor="#1a2332",
        padding=16,
        border_radius=10,
        on_click=lambda e, s=session_data: on_click(s) if on_click else None,
        ink=True if on_click else False,
    )


def StatsCard(
    title: str,
    value: str,
    subtitle: str = None,
    icon: str = None,
    color: str = "#4CAF50",
    on_click=None
) -> ft.Container:
    """Statistics card component"""
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(icon, size=24, color=color) if icon else ft.Container(),
                        ft.Text(
                            title,
                            size=12,
                            color="#8b95a5",
                            expand=True,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    value,
                    size=28,
                    weight=ft.FontWeight.W_700,
                    color=color,
                ),
                ft.Text(
                    subtitle,
                    size=11,
                    color="#8b95a5",
                ) if subtitle else ft.Container(),
            ],
            spacing=4,
        ),
        bgcolor="#1a2332",
        padding=16,
        border_radius=12,
        expand=True,
        on_click=on_click,
        ink=True if on_click else False,
    )


def AnalyticsCard(
    title: str,
    children: list,
    icon: str = None
) -> ft.Container:
    """Analytics section card"""
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(icon, size=20, color="#4CAF50") if icon else ft.Container(),
                        ft.Text(
                            title,
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color="#ffffff",
                        ),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color="#2d3a4d"),
                *children,
            ],
            spacing=12,
        ),
        bgcolor="#1a2332",
        padding=16,
        border_radius=12,
    )


def SettingsItem(
    title: str,
    subtitle: str = None,
    icon: str = None,
    trailing=None,
    on_click=None
) -> ft.Container:
    """Settings list item"""
    
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, size=22, color="#8b95a5") if icon else ft.Container(),
                ft.Column(
                    controls=[
                        ft.Text(
                            title,
                            size=15,
                            color="#ffffff",
                        ),
                        ft.Text(
                            subtitle,
                            size=12,
                            color="#8b95a5",
                        ) if subtitle else ft.Container(),
                    ],
                    spacing=2,
                    expand=True,
                ),
                trailing or ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color="#8b95a5"),
            ],
            spacing=12,
        ),
        padding=ft.padding.symmetric(vertical=12, horizontal=4),
        on_click=on_click,
        ink=True if on_click else False,
    )








