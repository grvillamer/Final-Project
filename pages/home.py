"""
SpottEd Home Page - Buildings Directory

Home shows a list of buildings. Tap a building to view its rooms, search by floor,
and (for instructors/admins) set schedules per room.
Shows room status summary (Available, Occupied, Under Maintenance).
"""

from __future__ import annotations

import flet as ft
from datetime import datetime

from database import db
from utils.helpers import get_initials
from utils.theme import get_theme


def HomePage(page: ft.Page, user: dict, on_navigate=None):
    """Home page showing buildings (instead of listing rooms directly)."""

    def t():
        return get_theme(page)

    c = t()

    user_name = user.get("first_name", "User")
    initials = get_initials(user.get("first_name", ""), user.get("last_name", ""))
    student_id = user.get("student_id", "")
    is_instructor = user.get("role") == "instructor"
    user_id = user.get("id")

    profile_picture = db.get_setting(user_id, "profile_picture", "") or None if user_id else None

    BUILDINGS = [
        "ACADEMIC BUILDING - I",
        "ACADEMIC BUILDING - II",
        "ACADEMIC BUILDING - III",
        "ACADEMIC BUILDING - IV",
        "ACADEMIC BUILDING - V",
        "GREEN BUILDING",
    ]

    search_state = {"value": ""}
    buildings_ref = ft.Ref[ft.Container]()

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

    def _get_room_status_counts(building: str) -> dict:
        """
        Get count of rooms by status for a building.
        Returns {'available': int, 'occupied': int, 'maintenance': int}
        """
        try:
            all_rooms = db.get_all_classrooms()
            building_rooms = [r for r in all_rooms if str(r.get("building", "")).strip() == building]

            available_count = 0
            occupied_count = 0
            maintenance_count = 0

            current_minutes = _get_current_time_minutes()

            for room in building_rooms:
                room_id = room.get("id")

                # Check if under maintenance
                if room.get("status") == "maintenance":
                    maintenance_count += 1
                    continue

                # Check for active schedules
                try:
                    schedules = db.get_room_schedules(room_id, datetime.now().strftime("%Y-%m-%d"))
                except:
                    schedules = []

                is_occupied = False
                for schedule in schedules:
                    start_minutes = _time_to_minutes(schedule.get("start_time", ""))
                    end_minutes = _time_to_minutes(schedule.get("end_time", ""))

                    if start_minutes <= current_minutes < end_minutes:
                        occupied_count += 1
                        is_occupied = True
                        break

                if not is_occupied:
                    available_count += 1

            return {
                'available': available_count,
                'occupied': occupied_count,
                'maintenance': maintenance_count,
            }
        except Exception:
            return {'available': 0, 'occupied': 0, 'maintenance': 0}

    def _rooms_count_by_building():
        try:
            rooms = db.get_all_classrooms()
        except Exception:
            rooms = []
        counts = {b: 0 for b in BUILDINGS}
        for r in rooms:
            b = str(r.get("building", "")).strip()
            if b in counts:
                counts[b] += 1
        return counts

    room_counts = _rooms_count_by_building()

    def _filtered_buildings():
        q = (search_state["value"] or "").strip().lower()
        if not q:
            return BUILDINGS
        return [b for b in BUILDINGS if q in b.lower()]

    def _open_building(building: str):
        if on_navigate:
            on_navigate("building_rooms", {"building": building})

    def _building_card(building: str):
        status_counts = _get_room_status_counts(building)
        available = status_counts['available']
        occupied = status_counts['occupied']
        maintenance = status_counts['maintenance']

        return ft.Container(
            content=ft.Column(
                [
                    # Building header with name and room count
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.APARTMENT, size=18, color=c["accent"]),
                                width=34,
                                height=34,
                                bgcolor=c["accent_bg"],
                                border_radius=10,
                                alignment=ft.alignment.center,
                            ),
                            ft.Column(
                                [
                                    ft.Text(building, size=14, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                                    ft.Text(f'{available + occupied + maintenance} rooms total', size=11, color=c["text_secondary"]),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=c["text_hint"]),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    # Status summary
                    ft.Row(
                        [
                            # Available
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(str(available), size=18, weight=ft.FontWeight.W_700, color="#4CAF50"),
                                        ft.Text("Available", size=9, color=c["text_secondary"]),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                ),
                                expand=True,
                            ),
                            ft.VerticalDivider(color=c["border"]),
                            # Occupied
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(str(occupied), size=18, weight=ft.FontWeight.W_700, color="#F44336"),
                                        ft.Text("Occupied", size=9, color=c["text_secondary"]),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                ),
                                expand=True,
                            ),
                            ft.VerticalDivider(color=c["border"]),
                            # Maintenance
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(str(maintenance), size=18, weight=ft.FontWeight.W_700, color="#FFC107"),
                                        ft.Text("Maintenance", size=9, color=c["text_secondary"]),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                ),
                                expand=True,
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                ],
                spacing=12,
            ),
            bgcolor=c["bg_card"],
            padding=14,
            border_radius=12,
            border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            on_click=lambda e, b=building: _open_building(b),
            ink=True,
        )

    def _refresh_buildings():
        buildings_ref.current.content = ft.Column(
            [_building_card(b) for b in _filtered_buildings()],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
        page.update()

    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text("CS", size=14, weight=ft.FontWeight.W_700, color="#ffffff"),
                                        width=36,
                                        height=36,
                                        bgcolor=c["accent"],
                                        border_radius=8,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("CSPC", size=12, weight=ft.FontWeight.W_700, color=c["accent"]),
                                            ft.Text("Building Directory", size=9, color=c["text_secondary"]),
                                        ],
                                        spacing=0,
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.Container(
                                content=(
                                    ft.Image(
                                        src=profile_picture,
                                        width=32,
                                        height=32,
                                        fit=ft.ImageFit.COVER,
                                    )
                                    if profile_picture
                                    else ft.Text(initials, size=12, weight=ft.FontWeight.W_600, color="#ffffff")
                                ),
                                width=32,
                                height=32,
                                bgcolor=None if profile_picture else c["accent"],
                                border_radius=16,
                                alignment=ft.alignment.center,
                                on_click=lambda e: on_navigate("profile") if on_navigate else None,
                                tooltip="View profile",
                                ink=True,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"Welcome, {user_name}", size=16, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                            ft.Row(
                                [
                                    ft.Text(student_id, size=11, color=c["text_secondary"]),
                                    ft.Container(
                                        content=ft.Text(
                                            "Instructor" if is_instructor else "Student",
                                            size=9,
                                            color="#ffffff",
                                            weight=ft.FontWeight.W_600,
                                        ),
                                        bgcolor=c["accent"] if is_instructor else c["info"],
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        border_radius=10,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=2,
                    ),
                    margin=ft.margin.only(top=8, bottom=12),
                ),
                ft.TextField(
                    hint_text="Search building...",
                    prefix_icon=ft.Icons.SEARCH,
                    on_change=lambda e: (search_state.__setitem__("value", e.control.value), _refresh_buildings()),
                    border_color=c["border"],
                    focused_border_color=c["accent"],
                    hint_style=ft.TextStyle(color=c["text_hint"], size=12),
                    text_style=ft.TextStyle(color=c["text_primary"]),
                    cursor_color=c["accent"],
                    border_radius=10,
                    content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    height=44,
                    bgcolor=c["bg_card"],
                ),
                ft.Container(height=10),
                ft.Container(
                    ref=buildings_ref,
                    content=ft.Column([_building_card(b) for b in BUILDINGS], spacing=10),
                    expand=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        bgcolor=c["bg_primary"],
        expand=True,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
    )

