"""
Smart Classroom - Admin Management Page
Implements user management with RBAC enforcement
"""
import flet as ft
from database import db
from utils.theme import get_theme
from utils.helpers import get_initials
from core.security import password_policy
from core.audit import audit_logger


def AdminPage(page: ft.Page, user: dict, on_navigate=None):
    """Admin dashboard for user management"""
    
    # RBAC Check - Only admins can access
    if user.get('role') != 'admin':
        audit_logger.log_access_denied(
            user.get('id'), 
            f"{user.get('first_name')} {user.get('last_name')}", 
            'Admin Panel', 
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
    users_list = ft.Ref[ft.Column]()
    search_field = ft.Ref[ft.TextField]()
    selected_tab = {"value": 0}
    
    def load_users():
        """Load and display users"""
        users = db.get_all_users(include_inactive=True)
        search_term = search_field.current.value.lower() if search_field.current else ""
        
        if users_list.current:
            users_list.current.controls.clear()
            
            for u in users:
                # Filter by search
                if search_term:
                    name = f"{u['first_name']} {u['last_name']}".lower()
                    if search_term not in name and search_term not in u['student_id'].lower() and search_term not in u['email'].lower():
                        continue
                
                # Skip current admin from list
                if u['id'] == user['id']:
                    continue
                
                is_active = u.get('is_active', 1)
                is_locked = u.get('failed_login_attempts', 0) >= 5
                
                # Role badge colors
                role_colors = {
                    'admin': '#f44336',
                    'instructor': '#2196F3',
                    'student': '#4CAF50'
                }
                
                users_list.current.controls.append(
                    ft.Container(
                        content=ft.Row([
                            # Avatar
                            ft.Container(
                                content=ft.Text(
                                    get_initials(u['first_name'], u['last_name']),
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color="#ffffff" if is_active else "#999999"
                                ),
                                width=40,
                                height=40,
                                bgcolor=role_colors.get(u['role'], '#9E9E9E') if is_active else '#BDBDBD',
                                border_radius=20,
                                alignment=ft.alignment.center,
                            ),
                            # User info
                            ft.Column([
                                ft.Row([
                                    ft.Text(
                                        f"{u['first_name']} {u['last_name']}", 
                                        size=14, 
                                        weight=ft.FontWeight.W_500,
                                        color=c["text_primary"] if is_active else c["text_hint"]
                                    ),
                                    ft.Container(
                                        content=ft.Text(u['role'].upper(), size=10, color="#ffffff"),
                                        bgcolor=role_colors.get(u['role'], '#9E9E9E'),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        border_radius=4,
                                    ),
                                    ft.Icon(ft.Icons.LOCK, size=14, color="#f44336") if is_locked else ft.Container(),
                                    ft.Icon(ft.Icons.BLOCK, size=14, color="#9E9E9E") if not is_active else ft.Container(),
                                ], spacing=8),
                                ft.Text(f"{u['student_id']} • {u['email']}", size=11, color=c["text_hint"]),
                            ], spacing=2, expand=True),
                            # Actions
                            ft.PopupMenuButton(
                                icon=ft.Icons.MORE_VERT,
                                icon_color=c["text_secondary"],
                                items=[
                                    ft.PopupMenuItem(
                                        text="View Details",
                                        icon=ft.Icons.PERSON,
                                        on_click=lambda e, uid=u['id']: show_user_details(uid),
                                    ),
                                    ft.PopupMenuItem(
                                        text="Change Role",
                                        icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                                        on_click=lambda e, uid=u['id'], role=u['role']: show_change_role_dialog(uid, role),
                                    ),
                                    ft.PopupMenuItem(
                                        text="Unlock Account" if is_locked else "Reset Password",
                                        icon=ft.Icons.LOCK_OPEN if is_locked else ft.Icons.PASSWORD,
                                        on_click=lambda e, uid=u['id'], locked=is_locked: unlock_or_reset(uid, locked),
                                    ),
                                    ft.PopupMenuItem(),  # Divider
                                    ft.PopupMenuItem(
                                        text="Enable Account" if not is_active else "Disable Account",
                                        icon=ft.Icons.CHECK_CIRCLE if not is_active else ft.Icons.CANCEL,
                                        on_click=lambda e, uid=u['id'], active=is_active: toggle_user_status(uid, active),
                                    ),
                                    ft.PopupMenuItem(
                                        text="Delete User",
                                        icon=ft.Icons.DELETE_FOREVER,
                                        on_click=lambda e, uid=u['id'], name=f"{u['first_name']} {u['last_name']}": show_delete_dialog(uid, name),
                                    ),
                                ],
                            ),
                        ], spacing=12),
                        bgcolor=c["bg_card"],
                        padding=12,
                        border_radius=10,
                        border=ft.border.all(1, c["border"]),
                    )
                )
            
            if len(users_list.current.controls) == 0:
                users_list.current.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=48, color=c["text_hint"]),
                            ft.Text("No users found", color=c["text_hint"]),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40,
                        alignment=ft.alignment.center,
                    )
                )
            
            page.update()
    
    def show_create_user_dialog(e):
        """Show dialog to create new user"""
        c = t()
        
        first_name_field = ft.Ref[ft.TextField]()
        last_name_field = ft.Ref[ft.TextField]()
        student_id_field = ft.Ref[ft.TextField]()
        email_field = ft.Ref[ft.TextField]()
        password_field = ft.Ref[ft.TextField]()
        role_dropdown = ft.Ref[ft.Dropdown]()
        error_text = ft.Ref[ft.Text]()
        password_strength = ft.Ref[ft.Container]()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def on_password_change(e):
            """Update password strength indicator"""
            password = password_field.current.value
            if password:
                score, label = password_policy.get_strength(password)
                colors = {'Weak': '#f44336', 'Fair': '#FF9800', 'Good': '#4CAF50', 'Strong': '#2196F3'}
                if password_strength.current:
                    password_strength.current.content = ft.Row([
                        ft.Container(width=score, height=4, bgcolor=colors.get(label, '#9E9E9E'), border_radius=2),
                        ft.Text(label, size=10, color=colors.get(label, c["text_hint"])),
                    ], spacing=8)
                    page.update()
        
        def create_user(e):
            first_name = first_name_field.current.value.strip()
            last_name = last_name_field.current.value.strip()
            student_id = student_id_field.current.value.strip()
            email = email_field.current.value.strip()
            password = password_field.current.value
            role = role_dropdown.current.value
            
            # Validation
            if not all([first_name, last_name, student_id, email, password]):
                error_text.current.value = "All fields are required"
                error_text.current.visible = True
                page.update()
                return
            
            # Validate password policy
            is_valid, errors = password_policy.validate(password, student_id)
            if not is_valid:
                error_text.current.value = errors[0]
                error_text.current.visible = True
                page.update()
                return
            
            # Create user
            new_user_id = db.create_user(student_id, email, password, first_name, last_name, role)
            
            if new_user_id:
                # Log the action
                audit_logger.log_user_create(
                    user['id'], 
                    f"{user['first_name']} {user['last_name']}",
                    new_user_id,
                    student_id,
                    role
                )
                
                dialog.open = False
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"User {first_name} {last_name} created successfully", color="#ffffff"),
                    bgcolor="#4CAF50",
                )
                page.snack_bar.open = True
                load_users()
            else:
                error_text.current.value = "Failed to create user. Student ID or email may already exist."
                error_text.current.visible = True
                page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create New User", size=18, weight=ft.FontWeight.W_600, color=c["text_primary"]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("", ref=error_text, size=12, color="#f44336", visible=False),
                    ft.Row([
                        ft.TextField(ref=first_name_field, label="First Name", expand=True,
                            border_color=c["border"], focused_border_color=c["accent"],
                            text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                        ft.TextField(ref=last_name_field, label="Last Name", expand=True,
                            border_color=c["border"], focused_border_color=c["accent"],
                            text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                    ], spacing=8),
                    ft.TextField(ref=student_id_field, label="Student/Employee ID",
                        border_color=c["border"], focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                    ft.TextField(ref=email_field, label="Email",
                        border_color=c["border"], focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                    ft.TextField(ref=password_field, label="Password", password=True, can_reveal_password=True,
                        border_color=c["border"], focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8,
                        on_change=on_password_change),
                    ft.Container(ref=password_strength, content=ft.Container(), height=20),
                    ft.Dropdown(ref=role_dropdown, label="Role", value="student",
                        options=[
                            ft.dropdown.Option("student", "Student"),
                            ft.dropdown.Option("instructor", "Instructor"),
                            ft.dropdown.Option("admin", "Administrator"),
                        ],
                        border_color=c["border"], focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                ], spacing=12),
                width=400,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Create User", bgcolor=c["accent"], color="#ffffff", on_click=create_user),
            ],
            bgcolor=c["bg_card"],
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_user_details(user_id: int):
        """Show user details dialog"""
        c = t()
        u = db.get_user(user_id)
        if not u:
            return
        
        activity = db.get_user_activity(user_id, limit=10)
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"{u['first_name']} {u['last_name']}", size=18, weight=ft.FontWeight.W_600, color=c["text_primary"]),
            content=ft.Container(
                content=ft.Column([
                    # User info
                    ft.Container(
                        content=ft.Column([
                            ft.Row([ft.Text("Student ID:", size=12, color=c["text_hint"], width=100),
                                   ft.Text(u['student_id'], size=12, color=c["text_primary"])]),
                            ft.Row([ft.Text("Email:", size=12, color=c["text_hint"], width=100),
                                   ft.Text(u['email'], size=12, color=c["text_primary"])]),
                            ft.Row([ft.Text("Role:", size=12, color=c["text_hint"], width=100),
                                   ft.Text(u['role'].upper(), size=12, color=c["text_primary"])]),
                            ft.Row([ft.Text("Status:", size=12, color=c["text_hint"], width=100),
                                   ft.Text("Active" if u.get('is_active', 1) else "Disabled", size=12, 
                                          color="#4CAF50" if u.get('is_active', 1) else "#f44336")]),
                            ft.Row([ft.Text("Last Login:", size=12, color=c["text_hint"], width=100),
                                   ft.Text(u.get('last_login', 'Never') or 'Never', size=12, color=c["text_primary"])]),
                            ft.Row([ft.Text("Failed Attempts:", size=12, color=c["text_hint"], width=100),
                                   ft.Text(str(u.get('failed_login_attempts', 0)), size=12, color=c["text_primary"])]),
                            ft.Row([ft.Text("Created:", size=12, color=c["text_hint"], width=100),
                                   ft.Text(u.get('created_at', 'Unknown'), size=12, color=c["text_primary"])]),
                        ], spacing=8),
                        bgcolor=c["bg_secondary"],
                        padding=12,
                        border_radius=8,
                    ),
                    ft.Container(height=12),
                    ft.Text("Recent Activity", size=14, weight=ft.FontWeight.W_500, color=c["text_primary"]),
                    ft.Container(
                        content=ft.Column([
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(a['activity_type'], size=11, color=c["text_primary"]),
                                    ft.Text(a['created_at'][:16], size=10, color=c["text_hint"]),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                padding=ft.padding.symmetric(vertical=4),
                            ) for a in activity
                        ] if activity else [ft.Text("No recent activity", size=12, color=c["text_hint"])]),
                        bgcolor=c["bg_secondary"],
                        padding=12,
                        border_radius=8,
                        height=150,
                    ),
                ], spacing=4),
                width=350,
            ),
            actions=[ft.TextButton("Close", on_click=close_dialog)],
            bgcolor=c["bg_card"],
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_change_role_dialog(user_id: int, current_role: str):
        """Show dialog to change user role"""
        c = t()
        role_dropdown = ft.Ref[ft.Dropdown]()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def change_role(e):
            new_role = role_dropdown.current.value
            if new_role and new_role != current_role:
                target_user = db.get_user(user_id)
                if db.change_user_role(user_id, new_role):
                    audit_logger.log_role_change(
                        user['id'],
                        f"{user['first_name']} {user['last_name']}",
                        user_id,
                        target_user['student_id'] if target_user else 'Unknown',
                        current_role,
                        new_role
                    )
                    dialog.open = False
                    page.snack_bar = ft.SnackBar(content=ft.Text("Role changed successfully", color="#ffffff"), bgcolor="#4CAF50")
                    page.snack_bar.open = True
                    load_users()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Change User Role", size=18, weight=ft.FontWeight.W_600, color=c["text_primary"]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Current role: {current_role.upper()}", size=12, color=c["text_hint"]),
                    ft.Dropdown(ref=role_dropdown, label="New Role", value=current_role,
                        options=[
                            ft.dropdown.Option("student", "Student"),
                            ft.dropdown.Option("instructor", "Instructor"),
                            ft.dropdown.Option("admin", "Administrator"),
                        ],
                        border_color=c["border"], focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                ], spacing=12),
                width=300,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Change Role", bgcolor=c["accent"], color="#ffffff", on_click=change_role),
            ],
            bgcolor=c["bg_card"],
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def toggle_user_status(user_id: int, is_active: bool):
        """Enable or disable user account"""
        target_user = db.get_user(user_id)
        if is_active:
            db.disable_user(user_id)
            action = "USER_DISABLE"
            msg = "User account disabled"
        else:
            db.enable_user(user_id)
            action = "USER_ENABLE"
            msg = "User account enabled"
        
        audit_logger.log(action, user['id'], f"{user['first_name']} {user['last_name']}", 
                        {'target_user': target_user['student_id'] if target_user else 'Unknown'})
        
        page.snack_bar = ft.SnackBar(content=ft.Text(msg, color="#ffffff"), bgcolor="#4CAF50")
        page.snack_bar.open = True
        load_users()
    
    def unlock_or_reset(user_id: int, is_locked: bool):
        """Unlock account or reset password"""
        if is_locked:
            db.unlock_user_account(user_id)
            audit_logger.log('ACCOUNT_UNLOCKED', user['id'], f"{user['first_name']} {user['last_name']}")
            page.snack_bar = ft.SnackBar(content=ft.Text("Account unlocked", color="#ffffff"), bgcolor="#4CAF50")
            page.snack_bar.open = True
            load_users()
        else:
            # Show reset password dialog
            show_reset_password_dialog(user_id)
    
    def show_reset_password_dialog(user_id: int):
        """Show dialog to reset user password"""
        c = t()
        password_field = ft.Ref[ft.TextField]()
        error_text = ft.Ref[ft.Text]()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def reset_password(e):
            new_password = password_field.current.value
            if not new_password:
                error_text.current.value = "Password is required"
                error_text.current.visible = True
                page.update()
                return
            
            is_valid, errors = password_policy.validate(new_password)
            if not is_valid:
                error_text.current.value = errors[0]
                error_text.current.visible = True
                page.update()
                return
            
            success, err = db.update_password(user_id, new_password, check_history=False)
            if success:
                audit_logger.log_password_change(user['id'], f"{user['first_name']} {user['last_name']}", forced=True)
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Password reset successfully", color="#ffffff"), bgcolor="#4CAF50")
                page.snack_bar.open = True
                page.update()
            else:
                error_text.current.value = err or "Failed to reset password"
                error_text.current.visible = True
                page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Reset User Password", size=18, weight=ft.FontWeight.W_600, color=c["text_primary"]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("", ref=error_text, size=12, color="#f44336", visible=False),
                    ft.TextField(ref=password_field, label="New Password", password=True, can_reveal_password=True,
                        border_color=c["border"], focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                    ft.Text("Password must be at least 8 characters with uppercase, lowercase, digit, and special character.",
                           size=10, color=c["text_hint"]),
                ], spacing=12),
                width=300,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Reset Password", bgcolor="#f44336", color="#ffffff", on_click=reset_password),
            ],
            bgcolor=c["bg_card"],
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_delete_dialog(user_id: int, user_name: str):
        """Show delete confirmation dialog"""
        c = t()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def delete_user(e):
            target_user = db.get_user(user_id)
            if db.delete_user(user_id):
                audit_logger.log_user_delete(
                    user['id'],
                    f"{user['first_name']} {user['last_name']}",
                    user_id,
                    target_user['student_id'] if target_user else 'Unknown'
                )
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("User deleted successfully", color="#ffffff"), bgcolor="#4CAF50")
                page.snack_bar.open = True
                load_users()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING, color="#f44336"),
                ft.Text("Delete User", size=18, weight=ft.FontWeight.W_600, color="#f44336"),
            ], spacing=8),
            content=ft.Text(f"Are you sure you want to permanently delete {user_name}? This action cannot be undone.",
                           color=c["text_secondary"]),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Delete", bgcolor="#f44336", color="#ffffff", on_click=delete_user),
            ],
            bgcolor=c["bg_card"],
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def go_back(e):
        if on_navigate:
            on_navigate('home')
    
    # Get stats
    user_counts = db.get_user_count_by_role()
    total_users = sum(user_counts.values())
    
    # Build UI
    content = ft.Column([
        # Header
        ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=c["text_primary"], on_click=go_back),
                ft.Text("User Management", size=20, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Add User",
                    icon=ft.Icons.PERSON_ADD,
                    bgcolor=c["accent"],
                    color="#ffffff",
                    on_click=show_create_user_dialog,
                ),
            ]),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        ),
        
        # Stats cards
        ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(total_users), size=24, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                        ft.Text("Total Users", size=11, color=c["text_hint"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    bgcolor=c["bg_card"],
                    padding=16,
                    border_radius=12,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(user_counts.get('admin', 0)), size=24, weight=ft.FontWeight.W_700, color="#f44336"),
                        ft.Text("Admins", size=11, color=c["text_hint"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    bgcolor=c["bg_card"],
                    padding=16,
                    border_radius=12,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(user_counts.get('instructor', 0)), size=24, weight=ft.FontWeight.W_700, color="#2196F3"),
                        ft.Text("Instructors", size=11, color=c["text_hint"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    bgcolor=c["bg_card"],
                    padding=16,
                    border_radius=12,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(user_counts.get('student', 0)), size=24, weight=ft.FontWeight.W_700, color="#4CAF50"),
                        ft.Text("Students", size=11, color=c["text_hint"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    bgcolor=c["bg_card"],
                    padding=16,
                    border_radius=12,
                    expand=True,
                ),
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=16),
        ),
        
        # Search
        ft.Container(
            content=ft.TextField(
                ref=search_field,
                hint_text="Search users...",
                prefix_icon=ft.Icons.SEARCH,
                border_color=c["border"],
                focused_border_color=c["accent"],
                text_style=ft.TextStyle(color=c["text_primary"]),
                hint_style=ft.TextStyle(color=c["text_hint"]),
                border_radius=10,
                on_change=lambda e: load_users(),
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        ),
        
        # Users list
        ft.Container(
            content=ft.Column(ref=users_list, scroll=ft.ScrollMode.AUTO, spacing=8),
            expand=True,
            padding=ft.padding.symmetric(horizontal=16),
        ),
    ], spacing=8, expand=True)
    
    # Load users on init
    page.on_view_pop = lambda e: load_users()
    
    # Initial load after a brief delay
    def init_load():
        load_users()
    
    page.run_task(init_load)
    
    return ft.Container(
        content=content,
        bgcolor=c["bg_primary"],
        expand=True,
    )

