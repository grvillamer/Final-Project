"""
Smart Classroom - Audit Log Viewer Page
Implements security audit log viewing with filters
"""
import flet as ft
from database import db
from utils.theme import get_theme
from core.audit import audit_logger


def AuditLogsPage(page: ft.Page, user: dict, on_navigate=None):
    """Audit log viewer for administrators"""
    
    # RBAC Check - Only admins can access
    if user.get('role') != 'admin':
        audit_logger.log_access_denied(
            user.get('id'), 
            f"{user.get('first_name')} {user.get('last_name')}", 
            'Audit Logs', 
            'admin'
        )
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.BLOCK, size=64, color="#f44336"),
                ft.Text("Access Denied", size=24, weight=ft.FontWeight.W_600, color="#f44336"),
                ft.Text("You don't have permission to access this page.", color="#666666"),
                ft.ElevatedButton("Go Back", on_click=lambda e: on_navigate('home') if on_navigate else None),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def t():
        return get_theme(page)
    
    c = t()
    
    # State
    logs_list = ft.Ref[ft.Column]()
    action_filter = ft.Ref[ft.Dropdown]()
    current_page = {"value": 0}
    page_size = 50
    
    def load_logs():
        """Load and display audit logs"""
        action = action_filter.current.value if action_filter.current and action_filter.current.value != "all" else None
        
        offset = current_page["value"] * page_size
        logs = db.get_audit_logs(limit=page_size, offset=offset, action_filter=action)
        
        if logs_list.current:
            logs_list.current.controls.clear()
            
            for log in logs:
                # Determine icon and color based on action
                action_icons = {
                    'LOGIN_SUCCESS': (ft.Icons.LOGIN, '#4CAF50'),
                    'LOGIN_FAILED': (ft.Icons.ERROR_OUTLINE, '#f44336'),
                    'LOGOUT': (ft.Icons.LOGOUT, '#9E9E9E'),
                    'PASSWORD_CHANGE': (ft.Icons.PASSWORD, '#2196F3'),
                    'USER_CREATE': (ft.Icons.PERSON_ADD, '#4CAF50'),
                    'USER_DELETE': (ft.Icons.PERSON_REMOVE, '#f44336'),
                    'USER_DISABLE': (ft.Icons.BLOCK, '#FF9800'),
                    'USER_ENABLE': (ft.Icons.CHECK_CIRCLE, '#4CAF50'),
                    'ROLE_CHANGE': (ft.Icons.ADMIN_PANEL_SETTINGS, '#9C27B0'),
                    'ACCOUNT_LOCKED': (ft.Icons.LOCK, '#f44336'),
                    'ACCOUNT_UNLOCKED': (ft.Icons.LOCK_OPEN, '#4CAF50'),
                    'ACCESS_DENIED': (ft.Icons.GAVEL, '#f44336'),
                    'PROFILE_UPDATE': (ft.Icons.EDIT, '#2196F3'),
                }
                
                icon, color = action_icons.get(log['action'], (ft.Icons.INFO, c["text_hint"]))
                success = log.get('success', 1)
                
                # Format timestamp
                timestamp = log.get('created_at', '')[:19] if log.get('created_at') else ''
                
                # Parse details
                details = log.get('details', '')
                if details:
                    try:
                        import json
                        details_dict = json.loads(details)
                        details = ', '.join([f"{k}: {v}" for k, v in details_dict.items()])
                    except:
                        pass
                
                logs_list.current.controls.append(
                    ft.Container(
                        content=ft.Row([
                            # Icon
                            ft.Container(
                                content=ft.Icon(icon, size=20, color="#ffffff"),
                                width=36,
                                height=36,
                                bgcolor=color if success else '#f44336',
                                border_radius=8,
                                alignment=ft.alignment.center,
                            ),
                            # Info
                            ft.Column([
                                ft.Row([
                                    ft.Text(log['action'].replace('_', ' ').title(), 
                                           size=13, weight=ft.FontWeight.W_500, color=c["text_primary"]),
                                    ft.Container(
                                        content=ft.Text("SUCCESS" if success else "FAILED", size=9, color="#ffffff"),
                                        bgcolor='#4CAF50' if success else '#f44336',
                                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                        border_radius=4,
                                    ),
                                ], spacing=8),
                                ft.Text(f"User: {log.get('username', 'System')} | {timestamp}", 
                                       size=11, color=c["text_hint"]),
                                ft.Text(details, size=10, color=c["text_secondary"]) if details else ft.Container(),
                            ], spacing=2, expand=True),
                            # Category badge
                            ft.Container(
                                content=ft.Text(log.get('category', 'Unknown')[:10], size=9, color=c["text_hint"]),
                                bgcolor=c["bg_secondary"],
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=4,
                            ),
                        ], spacing=12),
                        bgcolor=c["bg_card"],
                        padding=12,
                        border_radius=10,
                        border=ft.border.all(1, c["border"]),
                    )
                )
            
            if len(logs_list.current.controls) == 0:
                logs_list.current.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.HISTORY, size=48, color=c["text_hint"]),
                            ft.Text("No audit logs found", color=c["text_hint"]),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40,
                        alignment=ft.alignment.center,
                    )
                )
            
            page.update()
    
    def on_filter_change(e):
        """Handle filter change"""
        current_page["value"] = 0
        load_logs()
    
    def next_page(e):
        """Go to next page"""
        current_page["value"] += 1
        load_logs()
    
    def prev_page(e):
        """Go to previous page"""
        if current_page["value"] > 0:
            current_page["value"] -= 1
            load_logs()
    
    def go_back(e):
        if on_navigate:
            on_navigate('settings')
    
    # Get action types for filter
    action_types = db.get_audit_action_types()
    total_logs = db.get_audit_log_count()
    
    # Build UI
    content = ft.Column([
        # Header
        ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=c["text_primary"], on_click=go_back),
                ft.Text("Audit Logs", size=20, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text(f"{total_logs} total logs", size=12, color=c["text_hint"]),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    bgcolor=c["bg_card"],
                    border_radius=16,
                ),
            ]),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        ),
        
        # Summary cards
        ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.LOGIN, size=24, color="#4CAF50"),
                        ft.Text(str(db.get_audit_log_count(action_filter='LOGIN_SUCCESS')), 
                               size=18, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                        ft.Text("Logins", size=10, color=c["text_hint"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    bgcolor=c["bg_card"],
                    padding=12,
                    border_radius=10,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=24, color="#f44336"),
                        ft.Text(str(db.get_audit_log_count(action_filter='LOGIN_FAILED')), 
                               size=18, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                        ft.Text("Failed", size=10, color=c["text_hint"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    bgcolor=c["bg_card"],
                    padding=12,
                    border_radius=10,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON_ADD, size=24, color="#2196F3"),
                        ft.Text(str(db.get_audit_log_count(action_filter='USER_CREATE')), 
                               size=18, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                        ft.Text("Created", size=10, color=c["text_hint"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    bgcolor=c["bg_card"],
                    padding=12,
                    border_radius=10,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.GAVEL, size=24, color="#FF9800"),
                        ft.Text(str(db.get_audit_log_count(action_filter='ACCESS_DENIED')), 
                               size=18, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                        ft.Text("Denied", size=10, color=c["text_hint"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    bgcolor=c["bg_card"],
                    padding=12,
                    border_radius=10,
                    expand=True,
                ),
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=16),
        ),
        
        # Filter
        ft.Container(
            content=ft.Row([
                ft.Dropdown(
                    ref=action_filter,
                    label="Filter by Action",
                    value="all",
                    options=[ft.dropdown.Option("all", "All Actions")] + 
                            [ft.dropdown.Option(a, a.replace('_', ' ').title()) for a in action_types],
                    border_color=c["border"],
                    focused_border_color=c["accent"],
                    text_style=ft.TextStyle(color=c["text_primary"], size=12),
                    border_radius=8,
                    dense=True,
                    expand=True,
                    on_change=on_filter_change,
                ),
            ]),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        ),
        
        # Logs list
        ft.Container(
            content=ft.Column(ref=logs_list, scroll=ft.ScrollMode.AUTO, spacing=8),
            expand=True,
            padding=ft.padding.symmetric(horizontal=16),
        ),
        
        # Pagination
        ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    icon_color=c["text_primary"] if current_page["value"] > 0 else c["text_hint"],
                    on_click=prev_page,
                    disabled=current_page["value"] == 0,
                ),
                ft.Text(f"Page {current_page['value'] + 1}", size=12, color=c["text_secondary"]),
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    icon_color=c["text_primary"],
                    on_click=next_page,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=8),
        ),
    ], spacing=8, expand=True)
    
    # Initial load
    def init_load():
        load_logs()
    
    page.run_task(init_load)
    
    return ft.Container(
        content=content,
        bgcolor=c["bg_primary"],
        expand=True,
    )

