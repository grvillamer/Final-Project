"""
Reusable dialogs for room scheduling (Set Class Schedule).

Extracted from `pages/home.py` so other pages (e.g., building room list)
can reuse the same scheduling UI.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable, Optional

import flet as ft

from database import db
from utils.theme import get_theme


def show_set_class_dialog(
    *,
    page: ft.Page,
    user: dict,
    room: dict,
    on_success: Optional[Callable[[], None]] = None,
) -> None:
    """Show dialog for instructors/admins to set up a class schedule for a room."""
    c = get_theme(page)

    is_instructor = user.get("role") == "instructor"
    is_admin = user.get("role") == "admin"
    user_id = user.get("id")

    if not (is_instructor or is_admin):
        return

    subject_field = ft.Ref[ft.TextField]()
    day_dropdown = ft.Ref[ft.Dropdown]()
    start_time_dropdown = ft.Ref[ft.Dropdown]()
    end_time_dropdown = ft.Ref[ft.Dropdown]()
    semester_dropdown = ft.Ref[ft.Dropdown]()
    instructor_dropdown = ft.Ref[ft.Dropdown]()
    section_field = ft.Ref[ft.TextField]()
    error_text = ft.Ref[ft.Text]()
    availability_text = ft.Ref[ft.Text]()

    def _get_status_color(status: str) -> str:
        return {
            "available": "#4CAF50",
            "occupied": "#F44336",
            "maintenance": "#FFC107",
        }.get(status, c["text_secondary"])

    day_options = [
        ft.dropdown.Option("Monday", "Monday"),
        ft.dropdown.Option("Tuesday", "Tuesday"),
        ft.dropdown.Option("Wednesday", "Wednesday"),
        ft.dropdown.Option("Thursday", "Thursday"),
        ft.dropdown.Option("Friday", "Friday"),
        ft.dropdown.Option("Saturday", "Saturday"),
    ]

    time_options = []
    for hour in range(7, 21):
        time_str = f"{hour:02d}:00"
        if hour == 0:
            display = "12:00 AM"
        elif hour < 12:
            display = f"{hour:02d}:00 AM"
        elif hour == 12:
            display = "12:00 PM"
        else:
            display = f"{hour-12:02d}:00 PM"
        time_options.append(ft.dropdown.Option(time_str, display))

    semester_options = [
        ft.dropdown.Option("1st Semester 2025-2026", "1st Semester 2025-2026"),
        ft.dropdown.Option("2nd Semester 2025-2026", "2nd Semester 2025-2026"),
        ft.dropdown.Option("Summer 2026", "Summer 2026"),
    ]

    instructor_options = []
    if is_admin:
        instructors = db.get_users_by_role("instructor", include_inactive=False)
        instructor_options = [
            ft.dropdown.Option(
                str(u["id"]),
                f'{u["last_name"]}, {u["first_name"]} ({u["student_id"]})',
            )
            for u in instructors
        ]

    def close_dialog(_):
        dialog.open = False
        page.update()

    def check_availability(_=None):
        day = day_dropdown.current.value
        start = start_time_dropdown.current.value
        end = end_time_dropdown.current.value

        if not all([day, start, end]):
            availability_text.current.value = ""
            availability_text.current.visible = False
            page.update()
            return

        today = datetime.now()
        days_map = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
        }
        target_day = days_map.get(day, 0)
        days_ahead = target_day - today.weekday()
        if days_ahead < 0:
            days_ahead += 7
        next_date = today + timedelta(days=days_ahead)
        date_str = next_date.strftime("%Y-%m-%d")

        has_conflict = db.check_schedule_conflict(room["id"], date_str, start, end)
        if has_conflict:
            availability_text.current.value = "Room is OCCUPIED at this time"
            availability_text.current.color = c["error"]
        else:
            availability_text.current.value = "Room is AVAILABLE at this time"
            availability_text.current.color = c["success"]

        availability_text.current.visible = True
        page.update()

    def _parse_semester_range(label: str):
        if not label:
            return None
        label = label.strip()
        try:
            if label.startswith("1st Semester"):
                ay = label.split("1st Semester", 1)[1].strip()
                start_year = int(ay.split("-")[0])
                return datetime(start_year, 8, 1), datetime(start_year, 12, 31)
            if label.startswith("2nd Semester"):
                ay = label.split("2nd Semester", 1)[1].strip()
                start_year = int(ay.split("-")[0])
                end_year = start_year + 1
                return datetime(end_year, 1, 1), datetime(end_year, 5, 31)
            if label.startswith("Summer"):
                y = int(label.split("Summer", 1)[1].strip())
                return datetime(y, 6, 1), datetime(y, 7, 31)
        except Exception:
            return None
        return None

    def set_class(_):
        subject = (subject_field.current.value or "").strip()
        day = day_dropdown.current.value
        start_time = start_time_dropdown.current.value
        end_time = end_time_dropdown.current.value
        semester = semester_dropdown.current.value
        section = (section_field.current.value or "").strip()

        schedule_instructor_id = user_id
        if is_admin:
            if not instructor_dropdown.current or not instructor_dropdown.current.value:
                error_text.current.value = "Please select an instructor"
                error_text.current.visible = True
                page.update()
                return
            try:
                schedule_instructor_id = int(instructor_dropdown.current.value)
            except Exception:
                schedule_instructor_id = user_id

        if not subject:
            error_text.current.value = "Please enter a subject name"
            error_text.current.visible = True
            page.update()
            return
        if not day:
            error_text.current.value = "Please select a day"
            error_text.current.visible = True
            page.update()
            return
        if not start_time or not end_time:
            error_text.current.value = "Please select start and end time"
            error_text.current.visible = True
            page.update()
            return
        if start_time >= end_time:
            error_text.current.value = "End time must be after start time"
            error_text.current.visible = True
            page.update()
            return

        semester_range = _parse_semester_range(semester or "")
        if not semester_range:
            error_text.current.value = "Please select a valid semester"
            error_text.current.visible = True
            page.update()
            return

        start_date, end_date = semester_range
        days_map = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
        }
        target_day = days_map.get(day, 0)

        first = start_date
        days_ahead = (target_day - first.weekday()) % 7
        d = first + timedelta(days=days_ahead)

        dates = []
        while d <= end_date:
            dates.append(d.strftime("%Y-%m-%d"))
            d += timedelta(days=7)

        if not dates:
            error_text.current.value = "No matching dates found for this semester/day."
            error_text.current.visible = True
            page.update()
            return

        notes = f"Day: {day} | Semester: {semester or 'Not specified'}"
        if section:
            notes += f" | Section: {section}"

        created = 0
        conflicts = 0
        for date_str in dates:
            schedule_id = db.create_room_schedule(
                room_id=room["id"],
                instructor_id=schedule_instructor_id,
                subject_name=subject,
                schedule_date=date_str,
                start_time=start_time,
                end_time=end_time,
                notes=notes,
            )
            if schedule_id:
                created += 1
            else:
                conflicts += 1

        if created > 0:
            dialog.open = False
            msg = f"Scheduled {created} weekly sessions for {semester}."
            if conflicts:
                msg += f" ({conflicts} skipped due to conflicts)"
            page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=c["success"])
            page.snack_bar.open = True
            page.update()
            if on_success:
                on_success()
        else:
            error_text.current.value = "No schedules created (all dates conflicted)."
            error_text.current.visible = True
            page.update()

    room_status = room.get("status") or "available"
    if room.get("status") == "maintenance":
        room_status = "maintenance"

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SCHOOL, color=c["accent"], size=24),
                        ft.Text(
                            "Set Class Schedule",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=c["text_primary"],
                        ),
                    ],
                    spacing=8,
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=c["text_secondary"],
                    on_click=close_dialog,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.MEETING_ROOM, size=20, color=c["accent"]),
                                ft.Column(
                                    [
                                        ft.Text(
                                            room.get("name", "Room"),
                                            size=14,
                                            weight=ft.FontWeight.W_600,
                                            color=c["text_primary"],
                                        ),
                                        ft.Text(
                                            f'{room.get("code","")} • {room.get("building","")} • {room.get("floor","")} Floor',
                                            size=11,
                                            color=c["text_secondary"],
                                        ),
                                    ],
                                    spacing=0,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        str(room_status).upper(),
                                        size=9,
                                        color="#ffffff"
                                        if room_status != "maintenance"
                                        else "#000000",
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    bgcolor=_get_status_color(room_status),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                    border_radius=10,
                                ),
                            ],
                            spacing=10,
                        ),
                        bgcolor=c["accent_bg"],
                        padding=12,
                        border_radius=8,
                    ),
                    ft.Text("", ref=error_text, size=12, color=c["error"], visible=False),
                    ft.Text("", ref=availability_text, size=12, visible=False),
                    ft.TextField(
                        ref=subject_field,
                        label="Subject / Course Name",
                        hint_text="e.g., CC 101 - Introduction to Computing",
                        border_color=c["border"],
                        focused_border_color=c["accent"],
                        hint_style=ft.TextStyle(color=c["text_hint"]),
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        cursor_color=c["accent"],
                        border_radius=8,
                    ),
                    ft.TextField(
                        ref=section_field,
                        label="Section (Optional)",
                        hint_text="e.g., BSCS 3A",
                        border_color=c["border"],
                        focused_border_color=c["accent"],
                        hint_style=ft.TextStyle(color=c["text_hint"]),
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        cursor_color=c["accent"],
                        border_radius=8,
                    ),
                    ft.Dropdown(
                        ref=semester_dropdown,
                        label="Semester",
                        value="1st Semester 2025-2026",
                        options=semester_options,
                        border_color=c["border"],
                        focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        border_radius=8,
                    ),
                    ft.Dropdown(
                        ref=instructor_dropdown,
                        label="Instructor",
                        value=instructor_options[0].key if instructor_options else None,
                        options=instructor_options,
                        border_color=c["border"],
                        focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        border_radius=8,
                        visible=is_admin,
                    ),
                    ft.Dropdown(
                        ref=day_dropdown,
                        label="Day of Week",
                        options=day_options,
                        border_color=c["border"],
                        focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        border_radius=8,
                        on_change=check_availability,
                    ),
                    ft.Row(
                        [
                            ft.Dropdown(
                                ref=start_time_dropdown,
                                label="Start Time",
                                options=time_options,
                                border_color=c["border"],
                                focused_border_color=c["accent"],
                                text_style=ft.TextStyle(color=c["text_primary"]),
                                label_style=ft.TextStyle(color=c["text_secondary"]),
                                border_radius=8,
                                width=135,
                                on_change=check_availability,
                            ),
                            ft.Dropdown(
                                ref=end_time_dropdown,
                                label="End Time",
                                options=time_options,
                                border_color=c["border"],
                                focused_border_color=c["accent"],
                                text_style=ft.TextStyle(color=c["text_primary"]),
                                label_style=ft.TextStyle(color=c["text_secondary"]),
                                border_radius=8,
                                width=135,
                                on_change=check_availability,
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=300,
            height=420,
        ),
        actions=[
            ft.TextButton(
                "Cancel",
                on_click=close_dialog,
                style=ft.ButtonStyle(color=c["text_secondary"]),
            ),
            ft.ElevatedButton(
                "Set Class",
                bgcolor=c["accent"],
                color="#ffffff",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=set_class,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=c["bg_card"],
        shape=ft.RoundedRectangleBorder(radius=16),
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()

