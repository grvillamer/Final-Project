"""
SpottEd Activity Page - Recent Activity and History
"""
import flet as ft
from database import db
from datetime import datetime, timedelta
from utils.helpers import get_initials, time_ago
from utils.theme import get_theme


def ActivityPage(page: ft.Page, user: dict, on_navigate=None):
    """Recent activity page showing user's history"""
    
    def t():
        return get_theme(page)
    
    c = t()
    
    user_id = user.get('id')
    user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
    is_instructor = user.get('role') == 'instructor'
    
    # Refs
    activity_list_ref = ft.Ref[ft.Column]()
    
    # Get recent activities
    def get_activities():
        activities = []
        
        # Get user's recent schedules
        if is_instructor:
            schedules = db.get_instructor_schedules(user_id)
            for sched in schedules[:10]:
                activities.append({
                    "type": "schedule",
                    "icon": ft.Icons.EVENT,
                    "color": "#4CAF50",
                    "title": f"Scheduled: {sched.get('subject_name', 'Class')}",
                    "subtitle": f"{sched.get('room_name', 'Room')} • {sched.get('start_time', '')} - {sched.get('end_time', '')}",
                    "time": sched.get('schedule_date', ''),
                })
        
        # Add login activity
        activities.append({
            "type": "login",
            "icon": ft.Icons.LOGIN,
            "color": "#2196F3",
            "title": "Logged in to Smart Classroom",
            "subtitle": "Current session",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        
        # Add some sample activities
        activities.extend([
            {
                "type": "view",
                "icon": ft.Icons.VISIBILITY,
                "color": "#9C27B0",
                "title": "Viewed room availability",
                "subtitle": "CCS Building rooms",
                "time": (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M"),
            },
            {
                "type": "search",
                "icon": ft.Icons.SEARCH,
                "color": "#FF9800",
                "title": "Searched for available rooms",
                "subtitle": "Filter: All floors",
                "time": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
            },
        ])
        
        return activities
    
    activities_data = {"list": get_activities()}
    
    def build_activity_item(activity):
        c = t()
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(activity["icon"], size=20, color=activity["color"]),
                    width=40, height=40, bgcolor=c["bg_secondary"], border_radius=20,
                    alignment=ft.alignment.center,
                ),
                ft.Column([
                    ft.Text(activity["title"], size=13, weight=ft.FontWeight.W_500, color=c["text_primary"]),
                    ft.Text(activity["subtitle"], size=11, color=c["text_secondary"]),
                ], spacing=2, expand=True),
                ft.Column([
                    ft.Text(
                        time_ago(activity["time"]) if "T" in activity["time"] or " " in activity["time"] 
                        else activity["time"],
                        size=10, color=c["text_hint"]
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.END),
            ], spacing=12),
            bgcolor=c["bg_card"], padding=14, border_radius=12,
            border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
        )
    
    def build_stat_card(icon, value, label, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=24, color=color),
                ft.Text(str(value), size=20, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                ft.Text(label, size=10, color=c["text_secondary"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            bgcolor=c["bg_card"], padding=16, border_radius=12, expand=True,
            border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
        )
    
    def clear_activity_history(e):
        """Clear activity history with confirmation"""
        c = t()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def confirm_clear(e):
            dialog.open = False
            activities_data["list"] = []
            
            # Update the activity list UI
            if activity_list_ref.current:
                activity_list_ref.current.controls = [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.HISTORY, size=48, color=c["text_hint"]),
                            ft.Text("No activity yet", size=14, color=c["text_secondary"]),
                            ft.Text("Your recent actions will appear here", size=11, color=c["text_hint"]),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                        padding=40, alignment=ft.alignment.center,
                    )
                ]
            
            page.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#ffffff", size=18),
                    ft.Text("Activity history cleared", color="#ffffff"),
                ], spacing=8),
                bgcolor=c["accent"],
            )
            page.snack_bar.open = True
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Clear Activity History?", size=16, weight=ft.FontWeight.W_600, color=c["text_primary"]),
            content=ft.Text("This will remove all your activity history. This action cannot be undone.", 
                          size=13, color=c["text_secondary"]),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog, style=ft.ButtonStyle(color=c["text_secondary"])),
                ft.ElevatedButton("Clear", bgcolor=c["error"], color="#ffffff", on_click=confirm_clear),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    return ft.Container(
        content=ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Container(
                            content=ft.Text("CS", size=14, weight=ft.FontWeight.W_700, color="#ffffff"),
                            width=36, height=36, bgcolor=c["accent"], border_radius=8,
                            alignment=ft.alignment.center,
                        ),
                        ft.Column([
                            ft.Text("Recent Activity", size=16, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                            ft.Text("Your history and actions", size=11, color=c["text_secondary"]),
                        ], spacing=0),
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ),
            
            ft.Container(height=16),
            
            # Quick Stats
            ft.Row([
                build_stat_card(ft.Icons.CALENDAR_TODAY, len([a for a in activities_data["list"] if a["type"] == "schedule"]), "Bookings", "#4CAF50"),
                build_stat_card(ft.Icons.VISIBILITY, 5, "Views", "#9C27B0"),
                build_stat_card(ft.Icons.SEARCH, 3, "Searches", "#FF9800"),
            ], spacing=10),
            
            ft.Container(height=20),
            
            # Today's Activity
            ft.Row([
                ft.Text("Today", size=14, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                ft.Container(
                    content=ft.Text(datetime.now().strftime("%B %d, %Y"), size=11, color=c["text_secondary"]),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=10),
            
            # Activity list
            ft.Column(
                ref=activity_list_ref,
                controls=[build_activity_item(activity) for activity in activities_data["list"]],
                spacing=10,
            ),
            
            ft.Container(height=20),
            
            # Clear history button
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=c["text_secondary"]),
                    ft.Text("Clear Activity History", size=12, color=c["text_secondary"]),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                bgcolor=c["bg_card"], padding=12, border_radius=8,
                border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
                on_click=clear_activity_history,
                ink=True,
            ),
            
            ft.Container(height=20),
        ], scroll=ft.ScrollMode.AUTO, spacing=0),
        bgcolor=c["bg_primary"],
        expand=True,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
