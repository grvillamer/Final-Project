"""
SpottEd Navigation Components
"""
import flet as ft


def create_bottom_nav(page: ft.Page, selected_index: int = 0, on_change=None) -> ft.NavigationBar:
    """Create bottom navigation bar"""
    
    def handle_change(e):
        if on_change:
            on_change(e.control.selected_index)
    
    return ft.NavigationBar(
        selected_index=selected_index,
        on_change=handle_change,
        bgcolor="#1a2332",
        indicator_color="#2d3a4d",
        surface_tint_color="transparent",
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SCHOOL_OUTLINED,
                selected_icon=ft.Icons.SCHOOL,
                label="Classes",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.QR_CODE_SCANNER_OUTLINED,
                selected_icon=ft.Icons.QR_CODE_SCANNER,
                label="Scan",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ANALYTICS_OUTLINED,
                selected_icon=ft.Icons.ANALYTICS,
                label="Analytics",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
    )


def create_app_bar(title: str, page: ft.Page, show_back: bool = False, 
                   actions: list = None, on_back=None) -> ft.AppBar:
    """Create app bar with optional back button and actions"""
    
    def handle_back(e):
        if on_back:
            on_back()
        elif page.views and len(page.views) > 1:
            page.views.pop()
            page.update()
    
    leading = None
    if show_back:
        leading = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color="#ffffff",
            on_click=handle_back,
        )
    
    return ft.AppBar(
        leading=leading,
        title=ft.Text(
            title,
            size=20,
            weight=ft.FontWeight.W_600,
            color="#ffffff",
        ),
        center_title=True,
        bgcolor="#0d1520",
        actions=actions or [],
    )


def create_nav_item(icon: str, label: str, selected: bool = False, on_click=None) -> ft.Container:
    """Create a custom navigation item"""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(
                    name=icon,
                    color="#4CAF50" if selected else "#8b95a5",
                    size=24,
                ),
                ft.Text(
                    label,
                    size=11,
                    color="#4CAF50" if selected else "#8b95a5",
                    weight=ft.FontWeight.W_500 if selected else ft.FontWeight.W_400,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=ft.padding.symmetric(vertical=8, horizontal=16),
        on_click=on_click,
        ink=True,
    )



