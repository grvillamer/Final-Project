"""
SpottEd Map Page
Shows a campus map image and allows searching academic buildings.
"""

from __future__ import annotations

import flet as ft

from utils.theme import get_theme

BUILDINGS = [
    "ACADEMIC BUILDING - I",
    "ACADEMIC BUILDING - II",
    "ACADEMIC BUILDING - III",
    "ACADEMIC BUILDING - IV",
    "ACADEMIC BUILDING - V",
    "GREEN BUILDING",
]

MAP_IMAGE = "c__Users_admin_AppData_Roaming_Cursor_User_workspaceStorage_64e36a7c82f70fe09f47c4354aa9396d_images_image-a95b48df-3e04-45bb-aca8-41cd8f55b3d1.png"


def MapPage(page: ft.Page, user: dict, on_navigate=None):
    c = get_theme(page)
    search_value = {"value": ""}

    results_ref = ft.Ref[ft.Column]()
    no_results_ref = ft.Ref[ft.Container]()

    def _filtered_buildings():
        query = (search_value["value"] or "").strip().lower()
        if not query:
            return BUILDINGS
        return [b for b in BUILDINGS if query in b.lower()]

    def _open_building(building: str):
        if on_navigate:
            on_navigate("building_rooms", {"building": building})

    def _building_card(building: str):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(building, size=14, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                            ft.Text("Tap to view rooms", size=11, color=c["text_secondary"]),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color=c["text_hint"]),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=14,
            border_radius=12,
            bgcolor=c["bg_card"],
            border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            on_click=lambda e, b=building: _open_building(b),
            ink=True,
        )

    def _refresh():
        buildings = _filtered_buildings()
        if results_ref.current:
            results_ref.current.controls = [_building_card(building) for building in buildings]
        if no_results_ref.current:
            no_results_ref.current.visible = len(buildings) == 0
        page.update()

    content = ft.Column(
        [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text("Campus Map", size=20, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                        ft.Text("Search for Academic Buildings", size=12, color=c["text_secondary"]),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                margin=ft.margin.only(bottom=14),
            ),
            ft.TextField(
                hint_text="Search academic buildings...",
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
                expand=True,
            ),
            ft.Container(height=16),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Campus Site Plan", size=13, color=c["text_secondary"], weight=ft.FontWeight.W_600),
                        ft.Container(
                            content=ft.Image(
                                src=MAP_IMAGE,
                                fit=ft.ImageFit.CONTAIN,
                                width=600,
                                height=360,
                            ),
                            padding=ft.padding.all(12),
                            bgcolor=c["bg_card"],
                            border_radius=14,
                            border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
                        ),
                    ],
                    spacing=10,
                ),
                expand=True,
            ),
            ft.Container(height=16),
            ft.Text("Building search results", size=14, weight=ft.FontWeight.W_700, color=c["text_primary"]),
            ft.Column(
                [] if not BUILDINGS else [_building_card(building) for building in _filtered_buildings()],
                spacing=10,
                ref=results_ref,
            ),
            ft.Container(
                content=ft.Text("No academic buildings match your search.", size=12, color=c["text_hint"]),
                visible=not bool(_filtered_buildings()),
                margin=ft.margin.only(top=10),
                ref=no_results_ref,
            ),
        ],
        spacing=10,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    return content
