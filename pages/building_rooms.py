"""
SpottEd Building Rooms Page
Shows rooms within a building with search + floor filter.
Displays schedules, room status, and instructor information.
"""

from __future__ import annotations

import flet as ft
from datetime import datetime

from database import db
from utils.theme import get_theme
from pages.room_schedule_dialogs import show_set_class_dialog


def BuildingRoomsPage(
    page: ft.Page,
    user: dict,
    building_name: str,
    on_back=None,
) -> ft.Control:
    c = get_theme(page)

    is_instructor = user.get("role") == "instructor"
    is_admin = user.get("role") == "admin"

    search_value = {"value": ""}
    floor_value = {"value": "all"}

    search_ref = ft.Ref[ft.TextField]()
    floor_ref = ft.Ref[ft.Dropdown]()
    content_ref = ft.Ref[ft.Container]()

    def _get_status_color(status: str) -> str:
        """Get color for room status badge"""
        return {
            "available": "#4CAF50",      # Green
            "occupied": "#F44336",        # Red
            "maintenance": "#FFC107",     # Yellow/Amber
        }.get(status, "#2196F3")          # Blue default

    def _get_current_time_minutes() -> int:
        """Get current time in minutes since midnight"""
        now = datetime.now()
        return now.hour * 60 + now.minute

    def _time_to_minutes(time_str: str) -> int:
        """Convert HH:MM time string to minutes since midnight"""
        try:
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        except:
            return 0

    def _determine_room_status(room_id: int) -> tuple[str, str, str]:
        """
        Determine room status based on schedules and maintenance status.
        Returns (status, display_text, instructor_name)
        """
        # Check if room is under maintenance
        room = db.get_classroom(room_id)
        if room and room.get("status") == "maintenance":
            return ("maintenance", "Under Maintenance", "")

        # Get today's schedules for this room
        try:
            schedules = db.get_room_schedules(room_id, datetime.now().strftime("%Y-%m-%d"))
        except:
            schedules = []

        current_minutes = _get_current_time_minutes()

        # Check if any schedule is currently active
        for schedule in schedules:
            start_minutes = _time_to_minutes(schedule.get("start_time", ""))
            end_minutes = _time_to_minutes(schedule.get("end_time", ""))

            if start_minutes <= current_minutes < end_minutes:
                instructor_name = schedule.get("instructor_name", "Unknown Instructor")
                subject = schedule.get("subject_name", "Class")
                return ("occupied", f"Occupied - {subject}", instructor_name)

        # Check for upcoming schedule today
        for schedule in schedules:
            start_minutes = _time_to_minutes(schedule.get("start_time", ""))
            if start_minutes > current_minutes:
                subject = schedule.get("subject_name", "Class")
                start_time = schedule.get("start_time", "")
                return ("available", f"Available until {start_time}", "")

        # No schedules - available
        return ("available", "Available", "")

    def _load_rooms():
        rooms = db.get_all_classrooms()
        building_rooms = [r for r in rooms if str(r.get("building", "")).strip() == building_name]

        # normalize a few fields for display
        items = []
        for r in building_rooms:
            room_id = r.get("id")
            status, status_text, instructor_name = _determine_room_status(room_id)

            items.append(
                {
                    "id": room_id,
                    "name": r.get("name", ""),
                    "code": r.get("code", ""),
                    "building": r.get("building", ""),
                    "floor": r.get("floor", ""),
                    "capacity": r.get("capacity", 0),
                    "status": status,
                    "status_text": status_text,
                    "instructor_name": instructor_name,
                }
            )
        return items

    all_rooms = _load_rooms()
    unique_floors = sorted({str(r.get("floor", "")).strip() for r in all_rooms if str(r.get("floor", "")).strip()})

    def _filtered_rooms():
        rooms = all_rooms

        q = search_value["value"].strip().lower()
        if q:
            rooms = [
                r
                for r in rooms
                if q in str(r.get("name", "")).lower()
                or q in str(r.get("code", "")).lower()
                or q in str(r.get("floor", "")).lower()
            ]

        f = floor_value["value"]
        if f != "all":
            rooms = [r for r in rooms if str(r.get("floor", "")).strip() == f]

        # stable sort by code then name
        rooms = sorted(rooms, key=lambda r: (str(r.get("code", "")), str(r.get("name", ""))))
        return rooms

    def _refresh():
        content_ref.current.content = _build_list(_filtered_rooms())
        page.update()

    def _open_schedule(room: dict):
        show_set_class_dialog(
            page=page,
            user=user,
            room=room,
            on_success=lambda: None,
        )

    def _room_tile(idx: int, room: dict):
        title = room.get("name") or "Room"
        code = room.get("code") or ""
        floor = room.get("floor") or ""
        status = room.get("status", "available")
        status_text = room.get("status_text", "Available")
        instructor_name = room.get("instructor_name", "")
        can_set = bool(is_instructor or is_admin)

        # Status badge color
        status_color = _get_status_color(status)

        # Build content based on user role
        if is_instructor or is_admin:
            # Instructor/Admin view - shows schedule and Set Class button
            main_content = ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.MEETING_ROOM, size=18, color=c["accent"]),
                        width=34,
                        height=34,
                        bgcolor=c["accent_bg"],
                        border_radius=10,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(title, size=13, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                            ft.Row(
                                [
                                    ft.Text(code, size=11, color=c["text_secondary"]),
                                    ft.Text("•", size=11, color=c["text_hint"]),
                                    ft.Text(f"{floor} Floor", size=11, color=c["text_secondary"]),
                                ],
                                spacing=6,
                            ),
                            # Schedule and status row
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(status_text, size=10, color="#ffffff"),
                                        bgcolor=status_color,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=6,
                                    ),
                                    ft.Text(instructor_name, size=10, color=c["text_hint"]) if instructor_name else ft.SizedBox(),
                                ],
                                spacing=8,
                                wrap=True,
                            ) if status_text else ft.SizedBox(),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [ft.Icon(ft.Icons.ADD, size=14), ft.Text("Set", size=11)],
                            spacing=4,
                        ),
                        bgcolor=c["accent"],
                        color="#ffffff",
                        height=34,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=lambda e, r=room: _open_schedule(r),
                        visible=can_set,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=c["text_hint"]),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            # Student view - shows room info and schedule status
            main_content = ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.MEETING_ROOM, size=18, color=c["accent"]),
                        width=34,
                        height=34,
                        bgcolor=c["accent_bg"],
                        border_radius=10,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(title, size=13, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                            ft.Row(
                                [
                                    ft.Text(code, size=11, color=c["text_secondary"]),
                                    ft.Text("•", size=11, color=c["text_hint"]),
                                    ft.Text(f"{floor} Floor", size=11, color=c["text_secondary"]),
                                ],
                                spacing=6,
                            ),
                            # Schedule status for students
                            ft.Container(
                                content=ft.Text(status_text, size=10, color="#ffffff", weight=ft.FontWeight.W_600),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                border_radius=6,
                            ) if status_text else ft.SizedBox(),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=c["text_hint"]),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )

        return ft.Container(
            content=main_content,
            bgcolor=c["bg_card"],
            border_radius=12,
            padding=12,
            border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            on_click=(lambda e, r=room: _open_schedule(r)) if can_set else None,
            ink=True if can_set else False,
        )

    def _build_list(rooms: list[dict]):
        if not rooms:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.SEARCH_OFF, size=48, color=c["text_hint"]),
                        ft.Text("No rooms found", size=16, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                        ft.Text("Try changing search or floor filter.", size=12, color=c["text_secondary"]),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                padding=30,
            )
        return ft.Column([_room_tile(i, r) for i, r in enumerate(rooms)], spacing=10, scroll=ft.ScrollMode.AUTO)

    floor_options = [ft.dropdown.Option("all", "All Floors")] + [
        ft.dropdown.Option(f, f"{f}") for f in unique_floors
    ]

    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=c["text_primary"],
                    on_click=(lambda e: on_back() if on_back else None),
                ),
                ft.Column(
                    [
                        ft.Text(building_name, size=16, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                        ft.Text("Select a room to locate or set schedule", size=11, color=c["text_secondary"]),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        margin=ft.margin.only(bottom=10),
    )

    controls = ft.Column(
        [
            header,
            ft.TextField(
                ref=search_ref,
                hint_text="Search room name/code or floor...",
                prefix_icon=ft.Icons.SEARCH,
                on_change=lambda e: (search_value.__setitem__("value", e.control.value), _refresh()),
                border_color=c["border"],
                focused_border_color=c["accent"],
                hint_style=ft.TextStyle(color=c["text_hint"], size=12),
                text_style=ft.TextStyle(color=c["text_primary"]),
                cursor_color=c["accent"],
                border_radius=10,
                bgcolor=c["bg_card"],
                height=44,
                content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
            ),
            ft.Container(height=8),
            ft.Row(
                [
                    ft.Dropdown(
                        ref=floor_ref,
                        value="all",
                        options=floor_options,
                        on_change=lambda e: (floor_value.__setitem__("value", e.control.value), _refresh()),
                        border_color=c["border"],
                        focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"], size=11),
                        border_radius=10,
                        dense=True,
                        content_padding=10,
                        expand=True,
                    ),
                ],
                spacing=8,
            ),
            ft.Container(height=10),
            ft.Container(ref=content_ref, content=_build_list(_filtered_rooms()), expand=True),
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    return ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=controls,
                    width=min(page.width or 420, 520),
                    expand=True,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        ),
        bgcolor=c["bg_primary"],
        expand=True,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )

