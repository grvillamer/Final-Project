"""
SpottEd Theme Utilities - Light/Dark Mode Support
"""
import flet as ft


class AppTheme:
    """Theme colors for light and dark modes"""
    
    # Dark theme colors
    DARK = {
        "bg_primary": "#0d1520",
        "bg_secondary": "#1a2332",
        "bg_card": "#1a2332",
        "bg_input": "#1a2332",
        "text_primary": "#ffffff",
        "text_secondary": "#8b95a5",
        "text_hint": "#5a6474",
        "border": "#2d3a4d",
        "accent": "#4CAF50",
        "accent_bg": "#1a3d2e",
        "error": "#F44336",
        "warning": "#FFC107",
        "success": "#4CAF50",
        "info": "#2196F3",
        "nav_bg": "#1a2332",
        "divider": "#2d3a4d",
    }
    
    # Light theme colors
    LIGHT = {
        "bg_primary": "#f5f7fa",
        "bg_secondary": "#ffffff",
        "bg_card": "#ffffff",
        "bg_input": "#ffffff",
        "text_primary": "#1a2332",
        "text_secondary": "#5a6474",
        "text_hint": "#8b95a5",
        "border": "#e0e5ec",
        "accent": "#4CAF50",
        "accent_bg": "#e8f5e9",
        "error": "#F44336",
        "warning": "#FFC107",
        "success": "#4CAF50",
        "info": "#2196F3",
        "nav_bg": "#ffffff",
        "divider": "#e0e5ec",
    }
    
    @staticmethod
    def get_colors(page: ft.Page) -> dict:
        """Get theme colors based on current theme mode"""
        if page.theme_mode == ft.ThemeMode.LIGHT:
            return AppTheme.LIGHT
        return AppTheme.DARK
    
    @staticmethod
    def is_dark(page: ft.Page) -> bool:
        """Check if current theme is dark"""
        return page.theme_mode != ft.ThemeMode.LIGHT


def get_theme(page: ft.Page) -> dict:
    """Shorthand to get current theme colors"""
    return AppTheme.get_colors(page)






