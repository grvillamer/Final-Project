"""
SpottEd Settings Page - User Settings and Preferences
Fully Responsive with Expandable Sections
"""
import flet as ft
from database import db
from utils.helpers import get_initials
from utils.theme import get_theme


def SettingsPage(page: ft.Page, user: dict, on_navigate=None, on_logout=None):
    """Settings page with expandable sections - Fully Responsive"""
    
    user_id = user.get('id')
    user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
    email = user.get('email', '')
    student_id = user.get('student_id', '')
    role = user.get('role', 'student')
    initials = get_initials(user.get('first_name', ''), user.get('last_name', ''))
    phone = user.get('phone', '+63 912 345 6789')
    
    # Responsive breakpoints
    def get_responsive_values():
        width = page.width or 400
        if width < 480:  # Small mobile
            return {
                "max_width": None,
                "padding": 12,
                "dialog_width": min(width - 32, 300),
                "profile_size": 70,
                "logo_size": 60,
                "font_title": 15,
                "font_body": 12,
                "icon_size": 18,
                "button_padding": 10,
                "section_spacing": 8,
            }
        elif width < 600:  # Mobile
            return {
                "max_width": None,
                "padding": 16,
                "dialog_width": min(width - 40, 320),
                "profile_size": 80,
                "logo_size": 70,
                "font_title": 16,
                "font_body": 13,
                "icon_size": 20,
                "button_padding": 12,
                "section_spacing": 10,
            }
        elif width < 900:  # Tablet
            return {
                "max_width": 600,
                "padding": 24,
                "dialog_width": 380,
                "profile_size": 90,
                "logo_size": 80,
                "font_title": 17,
                "font_body": 14,
                "icon_size": 22,
                "button_padding": 14,
                "section_spacing": 12,
            }
        else:  # Desktop
            return {
                "max_width": 700,
                "padding": 32,
                "dialog_width": 420,
                "profile_size": 100,
                "logo_size": 90,
                "font_title": 18,
                "font_body": 14,
                "icon_size": 24,
                "button_padding": 16,
                "section_spacing": 14,
            }
    
    # Load settings
    settings = db.get_all_settings(user_id) if user_id else {}
    
    # Expanded states
    expanded = {
        "profile": False,
        "appearance": False,
        "language": False,
        "notifications": False,
        "privacy": False,
        "about": False,
    }
    
    # Refs for content containers
    refs = {
        "profile_content": ft.Ref[ft.Container](),
        "profile_arrow": ft.Ref[ft.Icon](),
        "appearance_content": ft.Ref[ft.Container](),
        "appearance_arrow": ft.Ref[ft.Icon](),
        "language_content": ft.Ref[ft.Container](),
        "language_arrow": ft.Ref[ft.Icon](),
        "notifications_content": ft.Ref[ft.Container](),
        "notifications_arrow": ft.Ref[ft.Icon](),
        "privacy_content": ft.Ref[ft.Container](),
        "privacy_arrow": ft.Ref[ft.Icon](),
        "about_content": ft.Ref[ft.Container](),
        "about_arrow": ft.Ref[ft.Icon](),
    }
    
    # Settings values
    settings_values = {
        "dark_mode": settings.get('theme', 'dark') == 'dark',
        "font_size": settings.get('font_size', 'Medium'),
        "compact_layout": settings.get('compact_layout', 'false') == 'true',
        "push_notifications": settings.get('push_notifications', 'true') == 'true',
        "class_reminders": settings.get('class_reminders', 'true') == 'true',
        "room_availability": settings.get('room_availability', 'false') == 'true',
        "profile_visibility": settings.get('profile_visibility', 'Public'),
        "data_sharing": settings.get('data_sharing', 'false') == 'true',
        "language": settings.get('language', 'English'),
    }
    
    def t():
        return get_theme(page)
    
    def go_back(e):
        if on_navigate:
            on_navigate('home')
    
    def save_setting(key, value):
        if user_id:
            db.set_setting(user_id, key, str(value))
    
    def refresh_page():
        page.bgcolor = t()["bg_primary"]
        if on_navigate:
            on_navigate('settings')
    
    def toggle_section(section_name):
        expanded[section_name] = not expanded[section_name]
        content_ref = refs[f"{section_name}_content"]
        arrow_ref = refs[f"{section_name}_arrow"]
        if content_ref.current:
            content_ref.current.visible = expanded[section_name]
        if arrow_ref.current:
            arrow_ref.current.name = ft.Icons.KEYBOARD_ARROW_DOWN if expanded[section_name] else ft.Icons.CHEVRON_RIGHT
        page.update()
    
    # Profile picture state
    profile_picture_path = {"value": settings.get('profile_picture', '')}
    profile_picture_display = ft.Ref[ft.Container]()
    
    # File picker for profile pictures
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file = e.files[0]
            profile_picture_path["value"] = file.path
            save_setting('profile_picture', file.path)
            
            page.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#ffffff", size=18),
                    ft.Text("Profile picture updated!", color="#ffffff"),
                ], spacing=8),
                bgcolor=c["success"],
            )
            page.snack_bar.open = True
            
            # Refresh the page to show new picture
            if on_navigate:
                on_navigate('settings')
    
    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)
    
    # ==================== CHANGE PROFILE PICTURE DIALOG ====================
    def show_profile_picture_dialog():
        c = t()
        rv = get_responsive_values()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def select_from_gallery(e):
            dialog.open = False
            page.update()
            # Open file picker for images
            file_picker.pick_files(
                allowed_extensions=["png", "jpg", "jpeg", "gif", "webp"],
                dialog_title="Select Profile Picture",
                file_type=ft.FilePickerFileType.IMAGE,
            )
        
        def take_photo(e):
            dialog.open = False
            page.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO, color="#ffffff", size=18),
                    ft.Text("Camera not available on this platform", color="#ffffff"),
                ], spacing=8),
                bgcolor=c["warning"],
            )
            page.snack_bar.open = True
            page.update()
        
        def remove_photo(e):
            dialog.open = False
            profile_picture_path["value"] = ""
            save_setting('profile_picture', '')
            
            page.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#ffffff", size=18),
                    ft.Text("Profile picture removed", color="#ffffff"),
                ], spacing=8),
                bgcolor=c["accent"],
            )
            page.snack_bar.open = True
            
            # Refresh page
            if on_navigate:
                on_navigate('settings')
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Change Profile Picture", size=rv["font_title"], weight=ft.FontWeight.W_600, color=c["text_primary"]),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PHOTO_LIBRARY, size=20, color=c["accent"]),
                            ft.Text("Choose from Gallery", size=rv["font_body"], color=c["text_primary"]),
                        ], spacing=12),
                        padding=ft.padding.symmetric(vertical=12),
                        on_click=select_from_gallery,
                        ink=True,
                    ),
                    ft.Divider(color=c["border"], height=1),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CAMERA_ALT, size=20, color=c["text_secondary"]),
                            ft.Text("Take a Photo", size=rv["font_body"], color=c["text_secondary"]),
                        ], spacing=12),
                        padding=ft.padding.symmetric(vertical=12),
                        on_click=take_photo,
                        ink=True,
                    ),
                    ft.Divider(color=c["border"], height=1),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DELETE_OUTLINE, size=20, color=c["error"]),
                            ft.Text("Remove Photo", size=rv["font_body"], color=c["error"]),
                        ], spacing=12),
                        padding=ft.padding.symmetric(vertical=12),
                        on_click=remove_photo,
                        ink=True,
                        visible=bool(profile_picture_path["value"]),
                    ),
                ], spacing=0),
                width=rv["dialog_width"],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog, style=ft.ButtonStyle(color=c["text_secondary"])),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== DELETE ACCOUNT DIALOG ====================
    def show_delete_account_dialog():
        c = t()
        rv = get_responsive_values()
        password_field = ft.Ref[ft.TextField]()
        error_text = ft.Ref[ft.Text]()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def confirm_delete(e):
            password = password_field.current.value
            
            if not password:
                error_text.current.value = "Please enter your password to confirm"
                error_text.current.visible = True
                page.update()
                return
            
            # Verify password
            verified_user = db.authenticate_user(student_id, password)
            if not verified_user:
                error_text.current.value = "Incorrect password"
                error_text.current.visible = True
                page.update()
                return
            
            # Delete the account
            success = db.delete_user(user_id)
            
            if success:
                dialog.open = False
                page.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="#ffffff", size=18),
                        ft.Text("Account deleted successfully", color="#ffffff"),
                    ], spacing=8),
                    bgcolor=c["success"],
                )
                page.snack_bar.open = True
                page.update()
                
                # Logout
                if on_logout:
                    on_logout()
            else:
                error_text.current.value = "Failed to delete account. Please try again."
                error_text.current.visible = True
                page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=c["error"], size=24),
                ft.Text("Delete Account", size=rv["font_title"], weight=ft.FontWeight.W_600, color=c["error"]),
            ], spacing=8),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "This action cannot be undone. All your data will be permanently deleted:",
                        size=rv["font_body"], color=c["text_secondary"],
                    ),
                    ft.Container(height=8),
                    ft.Row([ft.Icon(ft.Icons.CLOSE, size=14, color=c["error"]), 
                           ft.Text("Profile information", size=12, color=c["text_secondary"])], spacing=8),
                    ft.Row([ft.Icon(ft.Icons.CLOSE, size=14, color=c["error"]), 
                           ft.Text("Class schedules", size=12, color=c["text_secondary"])], spacing=8),
                    ft.Row([ft.Icon(ft.Icons.CLOSE, size=14, color=c["error"]), 
                           ft.Text("All settings", size=12, color=c["text_secondary"])], spacing=8),
                    ft.Container(height=16),
                    ft.Text("", ref=error_text, size=12, color=c["error"], visible=False),
                    ft.TextField(
                        ref=password_field,
                        label="Enter your password to confirm",
                        password=True, can_reveal_password=True,
                        border_color=c["border"], focused_border_color=c["error"],
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        cursor_color=c["error"], border_radius=8,
                    ),
                ], spacing=4),
                width=rv["dialog_width"],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog, style=ft.ButtonStyle(color=c["text_secondary"])),
                ft.ElevatedButton("Delete Account", bgcolor=c["error"], color="#ffffff",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== EDIT PROFILE DIALOG ====================
    def show_edit_profile_dialog(e):
        c = t()
        rv = get_responsive_values()
        first_name_field = ft.Ref[ft.TextField]()
        last_name_field = ft.Ref[ft.TextField]()
        phone_field = ft.Ref[ft.TextField]()
        error_text = ft.Ref[ft.Text]()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_profile(e):
            first_name = first_name_field.current.value.strip()
            last_name = last_name_field.current.value.strip()
            
            if not first_name or not last_name:
                error_text.current.value = "Please fill in all fields"
                error_text.current.visible = True
                page.update()
                return
            
            success = db.update_user(user_id, first_name=first_name, last_name=last_name)
            if success:
                user['first_name'] = first_name
                user['last_name'] = last_name
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Profile updated!"), bgcolor=c["success"])
                page.snack_bar.open = True
                refresh_page()
            else:
                error_text.current.value = "Failed to update"
                error_text.current.visible = True
                page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Profile", size=rv["font_title"], weight=ft.FontWeight.W_600, color=c["text_primary"]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("", ref=error_text, size=12, color=c["error"], visible=False),
                    ft.TextField(ref=first_name_field, value=user.get('first_name', ''), label="First Name",
                        border_color=c["border"], focused_border_color=c["accent"],
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                    ft.TextField(ref=last_name_field, value=user.get('last_name', ''), label="Last Name",
                        border_color=c["border"], focused_border_color=c["accent"],
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                    ft.TextField(ref=phone_field, value=phone, label="Phone Number", prefix_icon=ft.Icons.PHONE,
                        border_color=c["border"], focused_border_color=c["accent"],
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                ], spacing=12), width=rv["dialog_width"],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Save", bgcolor=c["accent"], color="#ffffff", on_click=save_profile),
            ],
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== CHANGE PASSWORD DIALOG ====================
    def show_change_password_dialog(e):
        c = t()
        rv = get_responsive_values()
        current_pw = ft.Ref[ft.TextField]()
        new_pw = ft.Ref[ft.TextField]()
        confirm_pw = ft.Ref[ft.TextField]()
        error_text = ft.Ref[ft.Text]()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def change_password(e):
            if not current_pw.current.value or not new_pw.current.value or not confirm_pw.current.value:
                error_text.current.value = "Please fill all fields"
                error_text.current.visible = True
                page.update()
                return
            if new_pw.current.value != confirm_pw.current.value:
                error_text.current.value = "Passwords don't match"
                error_text.current.visible = True
                page.update()
                return
            if len(new_pw.current.value) < 8:
                error_text.current.value = "Password must be 8+ characters"
                error_text.current.visible = True
                page.update()
                return
            
            verified = db.authenticate_user(student_id, current_pw.current.value)
            if not verified:
                error_text.current.value = "Current password incorrect"
                error_text.current.visible = True
                page.update()
                return
            
            if db.update_password(user_id, new_pw.current.value):
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Password changed!"), bgcolor=c["success"])
                page.snack_bar.open = True
                page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Change Password", size=rv["font_title"], weight=ft.FontWeight.W_600, color=c["text_primary"]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("", ref=error_text, size=12, color=c["error"], visible=False),
                    ft.TextField(ref=current_pw, label="Current Password", password=True, can_reveal_password=True,
                        border_color=c["border"], focused_border_color=c["accent"],
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                    ft.TextField(ref=new_pw, label="New Password", password=True, can_reveal_password=True,
                        border_color=c["border"], focused_border_color=c["accent"],
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                    ft.TextField(ref=confirm_pw, label="Confirm Password", password=True, can_reveal_password=True,
                        border_color=c["border"], focused_border_color=c["accent"],
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        text_style=ft.TextStyle(color=c["text_primary"]), border_radius=8),
                ], spacing=12), width=rv["dialog_width"],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Change", bgcolor=c["accent"], color="#ffffff", on_click=change_password),
            ],
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== LOGOUT DIALOG ====================
    def show_logout_dialog(e):
        c = t()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def confirm_logout(e):
            dialog.open = False
            page.update()
            if on_logout:
                on_logout()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Logout", size=18, weight=ft.FontWeight.W_600, color=c["text_primary"]),
            content=ft.Text("Are you sure you want to logout?", color=c["text_secondary"]),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Logout", bgcolor=c["error"], color="#ffffff", on_click=confirm_logout),
            ],
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== HELP & SUPPORT DIALOG ====================
    def show_help_support_dialog(e):
        c = t()
        rv = get_responsive_values()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        # Responsive FAQ item builder
        def build_faq_item(question, answer):
            return ft.Container(
                content=ft.Column([
                    ft.Text(question, size=rv["font_body"], color=c["text_primary"], weight=ft.FontWeight.W_500),
                    ft.Text(answer, size=max(10, rv["font_body"] - 2), color=c["text_secondary"]),
                ], spacing=4),
                padding=ft.padding.symmetric(vertical=8),
                border=ft.border.only(bottom=ft.BorderSide(1, c["border"])),
            )
        
        # Responsive support option builder
        def build_support_option(icon, title, subtitle, color):
            return ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=rv["icon_size"], color=color),
                        width=max(36, rv["icon_size"] + 16),
                        height=max(36, rv["icon_size"] + 16),
                        bgcolor=ft.Colors.with_opacity(0.1, color),
                        border_radius=8,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column([
                        ft.Text(title, size=rv["font_body"], color=c["text_primary"], weight=ft.FontWeight.W_500),
                        ft.Text(subtitle, size=max(9, rv["font_body"] - 3), color=c["text_hint"]),
                    ], spacing=2, expand=True),
                ], spacing=rv["section_spacing"]),
                padding=ft.padding.all(rv["button_padding"] - 2),
                bgcolor=c["bg_secondary"],
                border_radius=10,
            )
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.HELP_OUTLINE, size=rv["icon_size"], color=c["accent"]),
                ft.Text("Help & Support", size=rv["font_title"], weight=ft.FontWeight.W_600, color=c["text_primary"]),
            ], spacing=8),
            content=ft.Container(
                content=ft.Column([
                    # Support options - responsive grid
                    ft.Text("Contact Us", size=rv["font_body"], color=c["text_hint"], weight=ft.FontWeight.W_500),
                    ft.Container(height=4),
                    ft.ResponsiveRow([
                        ft.Container(
                            content=build_support_option(ft.Icons.EMAIL, "Email Support", "support@smartclass.edu", c["accent"]),
                            col={"xs": 12, "sm": 6},
                        ),
                        ft.Container(
                            content=build_support_option(ft.Icons.CHAT_BUBBLE_OUTLINE, "Live Chat", "Available 9AM-5PM", "#4CAF50"),
                            col={"xs": 12, "sm": 6},
                        ),
                    ], spacing=8, run_spacing=8),
                    ft.Container(height=rv["section_spacing"]),
                    
                    # FAQ Section
                    ft.Text("Frequently Asked Questions", size=rv["font_body"], color=c["text_hint"], weight=ft.FontWeight.W_500),
                    ft.Container(height=4),
                    ft.Container(
                        content=ft.Column([
                            build_faq_item(
                                "How do I mark attendance?",
                                "Go to the Attendance section, select your class, and use the QR scanner or manual entry."
                            ),
                            build_faq_item(
                                "Can I change my schedule?",
                                "Yes, go to Schedule > Edit to modify your class schedule and room assignments."
                            ),
                            build_faq_item(
                                "How do I reset my password?",
                                "Use the 'Forgot Password' option on the login screen or change it in Settings > Profile."
                            ),
                        ], spacing=0),
                        bgcolor=c["bg_secondary"],
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=rv["button_padding"], vertical=4),
                    ),
                ], spacing=4, scroll=ft.ScrollMode.AUTO),
                width=rv["dialog_width"],
                height=min(400, (page.height or 600) * 0.6),
            ),
            actions=[
                ft.TextButton("Close", on_click=close_dialog, style=ft.ButtonStyle(color=c["text_secondary"])),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== CONTACT DEVELOPER DIALOG ====================
    def show_contact_developer_dialog(e):
        c = t()
        rv = get_responsive_values()
        feedback_field = ft.Ref[ft.TextField]()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def send_feedback(e):
            feedback = feedback_field.current.value
            if feedback and feedback.strip():
                dialog.open = False
                page.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="#ffffff", size=18),
                        ft.Text("Thank you for your feedback!", color="#ffffff"),
                    ], spacing=8),
                    bgcolor=c["success"],
                )
                page.snack_bar.open = True
                page.update()
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please enter your feedback", color="#ffffff"),
                    bgcolor=c["warning"],
                )
                page.snack_bar.open = True
                page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.EMAIL_OUTLINED, size=rv["icon_size"], color="#4CAF50"),
                ft.Text("Contact Developer", size=rv["font_title"], weight=ft.FontWeight.W_600, color=c["text_primary"]),
            ], spacing=8),
            content=ft.Container(
                content=ft.Column([
                    # Developer info - responsive layout
                    ft.Container(
                        content=ft.ResponsiveRow([
                            ft.Container(
                                content=ft.Column([
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.CODE, size=rv["icon_size"] + 4, color="#4CAF50"),
                                        width=max(50, rv["logo_size"] * 0.7),
                                        height=max(50, rv["logo_size"] * 0.7),
                                        bgcolor=ft.Colors.with_opacity(0.1, "#4CAF50"),
                                        border_radius=max(25, rv["logo_size"] * 0.35),
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Text("Smart Classroom Team", size=rv["font_body"], color=c["text_primary"], weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                                    ft.Text("CCS Development Team", size=max(10, rv["font_body"] - 2), color=c["text_hint"], text_align=ft.TextAlign.CENTER),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                                col=12,
                                alignment=ft.alignment.center,
                            ),
                        ]),
                        padding=ft.padding.symmetric(vertical=rv["section_spacing"]),
                    ),
                    
                    # Contact options
                    ft.ResponsiveRow([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.EMAIL, size=rv["icon_size"] - 4, color=c["text_secondary"]),
                                ft.Text("dev@smartclassroom.edu", size=max(10, rv["font_body"] - 2), color=c["text_primary"]),
                            ], spacing=8),
                            col={"xs": 12, "sm": 6},
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.LANGUAGE, size=rv["icon_size"] - 4, color=c["text_secondary"]),
                                ft.Text("smartclassroom.edu", size=max(10, rv["font_body"] - 2), color=c["text_primary"]),
                            ], spacing=8),
                            col={"xs": 12, "sm": 6},
                        ),
                    ], spacing=8, run_spacing=8),
                    
                    ft.Container(height=rv["section_spacing"]),
                    ft.Divider(color=c["border"], height=1),
                    ft.Container(height=rv["section_spacing"]),
                    
                    # Feedback form
                    ft.Text("Send Feedback", size=rv["font_body"], color=c["text_hint"], weight=ft.FontWeight.W_500),
                    ft.Container(height=4),
                    ft.TextField(
                        ref=feedback_field,
                        multiline=True,
                        min_lines=3,
                        max_lines=5,
                        hint_text="Share your thoughts, suggestions, or report issues...",
                        border_color=c["border"],
                        focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"], size=rv["font_body"]),
                        hint_style=ft.TextStyle(color=c["text_hint"], size=rv["font_body"] - 1),
                        border_radius=10,
                    ),
                ], spacing=4),
                width=rv["dialog_width"],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog, style=ft.ButtonStyle(color=c["text_secondary"])),
                ft.ElevatedButton("Send", bgcolor="#4CAF50", color="#ffffff",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=send_feedback),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== TERMS OF SERVICE DIALOG ====================
    def show_terms_dialog(e):
        c = t()
        rv = get_responsive_values()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        terms_content = """1. Acceptance of Terms
By accessing and using Smart Classroom, you agree to be bound by these Terms of Service.

2. User Accounts
You are responsible for maintaining the confidentiality of your account credentials and for all activities under your account.

3. Acceptable Use
Users must not misuse the service, attempt unauthorized access, or interfere with other users' experience.

4. Privacy
Your use of the service is also governed by our Privacy Policy. We collect and process data as described therein.

5. Intellectual Property
All content, features, and functionality are owned by Smart Classroom and protected by applicable laws.

6. Modifications
We reserve the right to modify these terms at any time. Continued use constitutes acceptance of changes.

7. Limitation of Liability
Smart Classroom is provided "as is" without warranties. We are not liable for any damages arising from use.

8. Contact
For questions about these terms, contact us at legal@smartclassroom.edu"""
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=rv["icon_size"], color="#FF9800"),
                ft.Text("Terms of Service", size=rv["font_title"], weight=ft.FontWeight.W_600, color=c["text_primary"]),
            ], spacing=8),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(
                            terms_content,
                            size=max(10, rv["font_body"] - 1),
                            color=c["text_secondary"],
                        ),
                        bgcolor=c["bg_secondary"],
                        border_radius=10,
                        padding=rv["button_padding"],
                    ),
                ], scroll=ft.ScrollMode.AUTO),
                width=rv["dialog_width"],
                height=min(400, (page.height or 600) * 0.6),
            ),
            actions=[
                ft.TextButton("Close", on_click=close_dialog, style=ft.ButtonStyle(color=c["text_secondary"])),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== PRIVACY POLICY DIALOG ====================
    def show_privacy_dialog(e):
        c = t()
        rv = get_responsive_values()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        # Privacy info item builder
        def build_privacy_item(icon, title, description, color):
            return ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=rv["icon_size"] - 2, color=color),
                        width=max(32, rv["icon_size"] + 12),
                        height=max(32, rv["icon_size"] + 12),
                        bgcolor=ft.Colors.with_opacity(0.1, color),
                        border_radius=8,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column([
                        ft.Text(title, size=rv["font_body"], color=c["text_primary"], weight=ft.FontWeight.W_500),
                        ft.Text(description, size=max(9, rv["font_body"] - 2), color=c["text_hint"]),
                    ], spacing=2, expand=True),
                ], spacing=rv["section_spacing"], vertical_alignment=ft.CrossAxisAlignment.START),
                padding=ft.padding.symmetric(vertical=8),
            )
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.PRIVACY_TIP_OUTLINED, size=rv["icon_size"], color="#9C27B0"),
                ft.Text("Privacy Policy", size=rv["font_title"], weight=ft.FontWeight.W_600, color=c["text_primary"]),
            ], spacing=8),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "We are committed to protecting your privacy. Here's how we handle your data:",
                        size=rv["font_body"],
                        color=c["text_secondary"],
                    ),
                    ft.Container(height=rv["section_spacing"]),
                    
                    # Privacy items in responsive layout
                    ft.ResponsiveRow([
                        ft.Container(
                            content=build_privacy_item(
                                ft.Icons.SHIELD,
                                "Data Security",
                                "Your data is encrypted and stored securely on our servers.",
                                "#4CAF50"
                            ),
                            col={"xs": 12, "md": 6},
                        ),
                        ft.Container(
                            content=build_privacy_item(
                                ft.Icons.VISIBILITY_OFF,
                                "No Tracking",
                                "We don't track your browsing activity or sell your data.",
                                "#2196F3"
                            ),
                            col={"xs": 12, "md": 6},
                        ),
                        ft.Container(
                            content=build_privacy_item(
                                ft.Icons.PERSON,
                                "Your Control",
                                "You can delete your account and data at any time.",
                                "#FF9800"
                            ),
                            col={"xs": 12, "md": 6},
                        ),
                        ft.Container(
                            content=build_privacy_item(
                                ft.Icons.LOCK,
                                "Access Control",
                                "Only you can access your personal information.",
                                "#9C27B0"
                            ),
                            col={"xs": 12, "md": 6},
                        ),
                    ], spacing=4, run_spacing=4),
                    
                    ft.Container(height=rv["section_spacing"]),
                    ft.Divider(color=c["border"], height=1),
                    ft.Container(height=rv["section_spacing"]),
                    
                    # Data collection summary
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Data We Collect", size=rv["font_body"], color=c["text_primary"], weight=ft.FontWeight.W_500),
                            ft.Container(height=4),
                            ft.Row([ft.Icon(ft.Icons.CHECK, size=14, color=c["success"]), 
                                   ft.Text("Basic profile information", size=max(10, rv["font_body"] - 2), color=c["text_secondary"])], spacing=8),
                            ft.Row([ft.Icon(ft.Icons.CHECK, size=14, color=c["success"]), 
                                   ft.Text("Class schedules and attendance", size=max(10, rv["font_body"] - 2), color=c["text_secondary"])], spacing=8),
                            ft.Row([ft.Icon(ft.Icons.CHECK, size=14, color=c["success"]), 
                                   ft.Text("App usage for improvements", size=max(10, rv["font_body"] - 2), color=c["text_secondary"])], spacing=8),
                        ], spacing=4),
                        bgcolor=c["bg_secondary"],
                        border_radius=10,
                        padding=rv["button_padding"],
                    ),
                ], scroll=ft.ScrollMode.AUTO),
                width=rv["dialog_width"],
                height=min(420, (page.height or 600) * 0.65),
            ),
            actions=[
                ft.TextButton("Close", on_click=close_dialog, style=ft.ButtonStyle(color=c["text_secondary"])),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # Theme toggle handler
    def on_theme_toggle(e):
        settings_values["dark_mode"] = e.control.value
        save_setting('theme', 'dark' if e.control.value else 'light')
        if e.control.value:
            page.theme_mode = ft.ThemeMode.DARK
            page.bgcolor = "#0d1520"
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            page.bgcolor = "#f5f7fa"
        refresh_page()
    
    c = t()
    rv = get_responsive_values()
    
    # Container ref for dynamic updates
    main_container_ref = ft.Ref[ft.Container]()
    
    def build_section_header(icon, title, section_name, theme, responsive):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=responsive["icon_size"], color=theme["text_secondary"]),
                ft.Text(title, size=responsive["font_body"], color=theme["text_primary"], expand=True),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=responsive["icon_size"], color=theme["text_hint"], ref=refs[f"{section_name}_arrow"]),
            ], spacing=responsive["section_spacing"]),
            padding=ft.padding.symmetric(horizontal=responsive["padding"], vertical=responsive["button_padding"]),
            on_click=lambda e, s=section_name: toggle_section(s),
        )
    
    def build_toggle_row(icon, title, subtitle, value, on_change, theme, responsive):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=responsive["icon_size"] - 2, color=theme["text_secondary"]),
                ft.Column([
                    ft.Text(title, size=responsive["font_body"], color=theme["text_primary"]),
                    ft.Text(subtitle, size=max(9, responsive["font_body"] - 3), color=theme["text_hint"]) if subtitle else ft.Container(),
                ], spacing=0, expand=True),
                ft.Switch(value=value, active_color=theme["accent"], on_change=on_change, scale=0.9 if responsive["font_body"] < 13 else 1.0),
            ], spacing=responsive["section_spacing"]),
            padding=ft.padding.symmetric(horizontal=responsive["padding"], vertical=8),
        )
    
    def build_dropdown_row(icon, title, value, options, on_change, theme, responsive):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=responsive["icon_size"] - 2, color=theme["text_secondary"]),
                    ft.Text(title, size=responsive["font_body"], color=theme["text_primary"]),
                ], spacing=responsive["section_spacing"]),
                ft.Dropdown(
                    value=value,
                    options=[ft.dropdown.Option(o) for o in options],
                    border_color=theme["border"], focused_border_color=theme["accent"],
                    text_style=ft.TextStyle(color=theme["text_primary"], size=responsive["font_body"] - 1),
                    border_radius=8, content_padding=responsive["button_padding"] - 2, dense=True,
                    on_change=on_change,
                ),
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=responsive["padding"], vertical=8),
        )
    
    def build_link_row(icon, title, subtitle=None, on_click=None, theme=None, responsive=None):
        theme = theme or c
        responsive = responsive or rv
        # Calculate responsive values
        icon_size = responsive["icon_size"] - 2
        title_size = responsive["font_body"]
        subtitle_size = max(9, responsive["font_body"] - 3)
        h_padding = responsive["padding"]
        v_padding = max(10, responsive["button_padding"])
        spacing = responsive["section_spacing"]
        
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=icon_size, color=theme["text_secondary"]),
                    width=icon_size + 8,
                    alignment=ft.alignment.center,
                ),
                ft.Column([
                    ft.Text(
                        title, 
                        size=title_size, 
                        color=theme["text_primary"],
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        subtitle, 
                        size=subtitle_size, 
                        color=theme["text_hint"],
                    ) if subtitle else ft.Container(),
                ], spacing=2, expand=True),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=icon_size - 2, color=theme["text_hint"]),
            ], spacing=spacing, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=h_padding, vertical=v_padding),
            on_click=on_click,
            ink=True,
            border_radius=8,
        )
    
    # Build responsive content
    def build_settings_content():
        theme = t()
        responsive = get_responsive_values()
        
        # Info label size
        info_label_size = max(9, responsive["font_body"] - 2)
        
        settings_content = ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=theme["text_primary"], icon_size=responsive["icon_size"], on_click=go_back),
                    ft.Text("Settings", size=responsive["font_title"], weight=ft.FontWeight.W_600, color=theme["text_primary"]),
                ], spacing=8),
                margin=ft.margin.only(bottom=responsive["section_spacing"]),
            ),
            
            # ==================== PROFILE INFORMATION ====================
            ft.Container(
                content=ft.Column([
                    build_section_header(ft.Icons.PERSON_OUTLINE, "Profile Information", "profile", theme, responsive),
                    ft.Container(
                        ref=refs["profile_content"],
                        content=ft.Column([
                            ft.Divider(color=theme["border"], height=1),
                            # Profile picture
                            ft.Container(
                                content=ft.Column([
                                    ft.Stack([
                                        ft.Container(
                                            content=ft.Text(initials, size=responsive["profile_size"] * 0.35, weight=ft.FontWeight.W_600, color="#000000"),
                                            width=responsive["profile_size"], height=responsive["profile_size"], bgcolor="#FFC107", border_radius=responsive["profile_size"] / 2,
                                            alignment=ft.alignment.center,
                                        ),
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.CAMERA_ALT, size=max(12, responsive["icon_size"] - 6), color="#ffffff"),
                                            width=max(22, responsive["icon_size"] + 4), height=max(22, responsive["icon_size"] + 4), bgcolor="#2196F3", border_radius=max(11, (responsive["icon_size"] + 4) / 2),
                                            alignment=ft.alignment.center, right=0, bottom=0,
                                        ),
                                    ], width=responsive["profile_size"], height=responsive["profile_size"]),
                                    ft.Text("Tap to change profile picture", size=info_label_size, color=theme["text_hint"]),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                                padding=ft.padding.symmetric(vertical=responsive["button_padding"]),
                                alignment=ft.alignment.center,
                                on_click=lambda e: show_profile_picture_dialog(),
                                ink=True,
                            ),
                            # Info rows
                            ft.Container(
                                content=ft.Column([
                                    ft.Column([ft.Text("Full Name", size=info_label_size, color=theme["text_hint"]),
                                              ft.Text(user_name, size=responsive["font_body"], color=theme["text_primary"])], spacing=2),
                                    ft.Container(height=responsive["section_spacing"]),
                                    ft.Column([ft.Text("Student ID", size=info_label_size, color=theme["text_hint"]),
                                              ft.Text(student_id, size=responsive["font_body"], color=theme["text_primary"])], spacing=2),
                                    ft.Container(height=responsive["section_spacing"]),
                                    ft.Column([ft.Text("Email", size=info_label_size, color=theme["text_hint"]),
                                              ft.Text(email, size=responsive["font_body"], color=theme["text_primary"])], spacing=2),
                                    ft.Container(height=responsive["section_spacing"]),
                                    ft.Column([ft.Text("Phone Number", size=info_label_size, color=theme["text_hint"]),
                                              ft.Text(phone, size=responsive["font_body"], color=theme["text_primary"])], spacing=2),
                                ]),
                                padding=ft.padding.symmetric(horizontal=responsive["padding"]),
                            ),
                            ft.Container(height=responsive["section_spacing"]),
                            # Buttons
                            ft.Container(
                                content=ft.Column([
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.EDIT_OUTLINED, size=responsive["icon_size"] - 4, color=theme["text_primary"]),
                                            ft.Text("Edit Profile", size=responsive["font_body"] - 1, color=theme["text_primary"]),
                                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                                        bgcolor=theme["bg_secondary"], padding=responsive["button_padding"], border_radius=8,
                                        border=ft.border.all(1, theme["border"]), on_click=show_edit_profile_dialog,
                                    ),
                                    ft.Container(height=8),
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.LOCK_OUTLINE, size=responsive["icon_size"] - 4, color=theme["text_primary"]),
                                            ft.Text("Change Password", size=responsive["font_body"] - 1, color=theme["text_primary"]),
                                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                                        bgcolor=theme["bg_secondary"], padding=responsive["button_padding"], border_radius=8,
                                        border=ft.border.all(1, theme["border"]), on_click=show_change_password_dialog,
                                    ),
                                ]),
                                padding=ft.padding.symmetric(horizontal=responsive["padding"]),
                            ),
                            ft.Container(height=responsive["padding"]),
                        ]),
                        visible=False,
                    ),
                ]),
                bgcolor=theme["bg_card"], border_radius=12,
                border=ft.border.all(1, theme["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            ),
            
            ft.Container(height=responsive["section_spacing"]),
            
            # ==================== APPEARANCE ====================
            ft.Container(
                content=ft.Column([
                    build_section_header(ft.Icons.PALETTE_OUTLINED, "Appearance", "appearance", theme, responsive),
                    ft.Container(
                        ref=refs["appearance_content"],
                        content=ft.Column([
                            ft.Divider(color=theme["border"], height=1),
                            build_toggle_row(ft.Icons.DARK_MODE, "Theme", "Dark Mode" if settings_values["dark_mode"] else "Light Mode",
                                           settings_values["dark_mode"], on_theme_toggle, theme, responsive),
                            build_dropdown_row(ft.Icons.TEXT_FIELDS, "Font Size", settings_values["font_size"],
                                             ["Small", "Medium", "Large"],
                                             lambda e: save_setting('font_size', e.control.value), theme, responsive),
                            build_toggle_row(ft.Icons.VIEW_COMPACT, "Compact Layout", "More content in less space",
                                           settings_values["compact_layout"],
                                           lambda e: save_setting('compact_layout', str(e.control.value).lower()), theme, responsive),
                            ft.Container(height=8),
                        ]),
                        visible=False,
                    ),
                ]),
                bgcolor=theme["bg_card"], border_radius=12,
                border=ft.border.all(1, theme["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            ),
            
            ft.Container(height=responsive["section_spacing"]),
            
            # ==================== LANGUAGE ====================
            ft.Container(
                content=ft.Column([
                    build_section_header(ft.Icons.LANGUAGE, "Language", "language", theme, responsive),
                    ft.Container(
                        ref=refs["language_content"],
                        content=ft.Column([
                            ft.Divider(color=theme["border"], height=1),
                            build_dropdown_row(ft.Icons.TRANSLATE, "App Language", settings_values["language"],
                                             ["English", "Filipino", "Cebuano", "Bikol"],
                                             lambda e: save_setting('language', e.control.value), theme, responsive),
                            ft.Container(height=8),
                        ]),
                        visible=False,
                    ),
                ]),
                bgcolor=theme["bg_card"], border_radius=12,
                border=ft.border.all(1, theme["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            ),
            
            ft.Container(height=responsive["section_spacing"]),
            
            # ==================== NOTIFICATIONS ====================
            ft.Container(
                content=ft.Column([
                    build_section_header(ft.Icons.NOTIFICATIONS_OUTLINED, "Notifications", "notifications", theme, responsive),
                    ft.Container(
                        ref=refs["notifications_content"],
                        content=ft.Column([
                            ft.Divider(color=theme["border"], height=1),
                            build_toggle_row(ft.Icons.NOTIFICATIONS_ACTIVE, "Push Notifications", "Receive app notifications",
                                           settings_values["push_notifications"],
                                           lambda e: save_setting('push_notifications', str(e.control.value).lower()), theme, responsive),
                            build_toggle_row(ft.Icons.ALARM, "Class Reminders", "Get notified before scheduled classes",
                                           settings_values["class_reminders"],
                                           lambda e: save_setting('class_reminders', str(e.control.value).lower()), theme, responsive),
                            build_toggle_row(ft.Icons.MEETING_ROOM, "Room Availability", "Notify when rooms become available",
                                           settings_values["room_availability"],
                                           lambda e: save_setting('room_availability', str(e.control.value).lower()), theme, responsive),
                            ft.Container(height=8),
                        ]),
                        visible=False,
                    ),
                ]),
                bgcolor=theme["bg_card"], border_radius=12,
                border=ft.border.all(1, theme["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            ),
            
            ft.Container(height=responsive["section_spacing"]),
            
            # ==================== PRIVACY & SECURITY ====================
            ft.Container(
                content=ft.Column([
                    build_section_header(ft.Icons.SHIELD_OUTLINED, "Privacy & Security", "privacy", theme, responsive),
                    ft.Container(
                        ref=refs["privacy_content"],
                        content=ft.Column([
                            ft.Divider(color=theme["border"], height=1),
                            build_dropdown_row(ft.Icons.VISIBILITY, "Profile Visibility", settings_values["profile_visibility"],
                                             ["Public", "Students Only", "Private"],
                                             lambda e: save_setting('profile_visibility', e.control.value), theme, responsive),
                            build_toggle_row(ft.Icons.SHARE, "Data Sharing", "Share usage data for improvements",
                                           settings_values["data_sharing"],
                                           lambda e: save_setting('data_sharing', str(e.control.value).lower()), theme, responsive),
                            build_link_row(ft.Icons.LOCK, "App Permissions", on_click=lambda e: None, theme=theme, responsive=responsive),
                            ft.Container(height=8),
                        ]),
                        visible=False,
                    ),
                ]),
                bgcolor=theme["bg_card"], border_radius=12,
                border=ft.border.all(1, theme["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            ),
            
            ft.Container(height=responsive["section_spacing"]),
            
            # ==================== ADMIN PANEL (Admin Only) ====================
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=responsive["icon_size"], color="#f44336"),
                            ft.Text("Admin Panel", size=responsive["font_body"], color=theme["text_primary"], expand=True),
                            ft.Container(
                                content=ft.Text("ADMIN", size=9, color="#ffffff"),
                                bgcolor="#f44336",
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                border_radius=4,
                            ),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=responsive["icon_size"], color=theme["text_hint"]),
                        ], spacing=responsive["section_spacing"]),
                        padding=ft.padding.symmetric(horizontal=responsive["padding"], vertical=responsive["button_padding"]),
                        on_click=lambda e: on_navigate('admin') if on_navigate else None,
                    ),
                    ft.Divider(color=theme["border"], height=1),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PEOPLE, size=responsive["icon_size"] - 2, color=theme["text_secondary"]),
                            ft.Column([
                                ft.Text("User Management", size=responsive["font_body"], color=theme["text_primary"]),
                                ft.Text("Create, edit, and manage users", size=max(9, responsive["font_body"] - 3), color=theme["text_hint"]),
                            ], spacing=2, expand=True),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=responsive["icon_size"] - 4, color=theme["text_hint"]),
                        ], spacing=responsive["section_spacing"]),
                        padding=ft.padding.symmetric(horizontal=responsive["padding"], vertical=10),
                        on_click=lambda e: on_navigate('admin') if on_navigate else None,
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.HISTORY, size=responsive["icon_size"] - 2, color=theme["text_secondary"]),
                            ft.Column([
                                ft.Text("Audit Logs", size=responsive["font_body"], color=theme["text_primary"]),
                                ft.Text("View security and activity logs", size=max(9, responsive["font_body"] - 3), color=theme["text_hint"]),
                            ], spacing=2, expand=True),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=responsive["icon_size"] - 4, color=theme["text_hint"]),
                        ], spacing=responsive["section_spacing"]),
                        padding=ft.padding.symmetric(horizontal=responsive["padding"], vertical=10),
                        on_click=lambda e: on_navigate('audit_logs') if on_navigate else None,
                    ),
                ]),
                bgcolor=theme["bg_card"], border_radius=12,
                border=ft.border.all(1, theme["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
                visible=role == 'admin',  # Only visible for admins
            ),
            
            ft.Container(height=responsive["section_spacing"], visible=role == 'admin'),
            
            # ==================== ABOUT APP ====================
            ft.Container(
                content=ft.Column([
                    build_section_header(ft.Icons.INFO_OUTLINE, "About App", "about", theme, responsive),
                    ft.Container(
                        ref=refs["about_content"],
                        content=ft.Column([
                            ft.Divider(color=theme["border"], height=1),
                            # App logo and info - responsive centered layout
                            ft.Container(
                                content=ft.Column([
                                    # Logo container with responsive size
                                    ft.Container(
                                        content=ft.Text(
                                            "SC", 
                                            size=responsive["logo_size"] * 0.28, 
                                            weight=ft.FontWeight.W_700, 
                                            color="#ffffff"
                                        ),
                                        width=responsive["logo_size"], 
                                        height=responsive["logo_size"], 
                                        bgcolor="#2196F3", 
                                        border_radius=responsive["logo_size"] * 0.18,
                                        alignment=ft.alignment.center,
                                        shadow=ft.BoxShadow(
                                            spread_radius=0,
                                            blur_radius=8,
                                            color=ft.Colors.with_opacity(0.3, "#2196F3"),
                                            offset=ft.Offset(0, 4),
                                        ),
                                    ),
                                    ft.Container(height=responsive["section_spacing"]),
                                    # App name - responsive font
                                    ft.Text(
                                        "Smart Classroom", 
                                        size=responsive["font_title"] + 2, 
                                        weight=ft.FontWeight.W_600, 
                                        color=theme["text_primary"],
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    # Version text
                                    ft.Text(
                                        "Version 1.0.0", 
                                        size=info_label_size, 
                                        color=theme["text_hint"],
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                                padding=ft.padding.symmetric(vertical=responsive["padding"]),
                                alignment=ft.alignment.center,
                            ),
                            # Divider before links
                            ft.Container(
                                content=ft.Divider(color=theme["border"], height=1),
                                padding=ft.padding.symmetric(horizontal=responsive["padding"]),
                            ),
                            # Feature links - responsive grid layout with centered cards
                            ft.Container(
                                content=ft.ResponsiveRow([
                                    # Help & Support
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.HELP_OUTLINE, size=responsive["icon_size"] + 4, color=theme["accent"]),
                                                width=50,
                                                height=50,
                                                bgcolor=ft.Colors.with_opacity(0.1, theme["accent"]),
                                                border_radius=12,
                                                alignment=ft.alignment.center,
                                            ),
                                            ft.Container(height=8),
                                            ft.Text("Help & Support", size=responsive["font_body"], color=theme["text_primary"], weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER),
                                            ft.Text("Get help and contact support", size=max(9, responsive["font_body"] - 3), color=theme["text_hint"], text_align=ft.TextAlign.CENTER),
                                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                                        padding=ft.padding.all(responsive["button_padding"]),
                                        border_radius=12,
                                        bgcolor=theme["bg_secondary"],
                                        on_click=show_help_support_dialog,
                                        ink=True,
                                        alignment=ft.alignment.center,
                                        col={"xs": 6, "sm": 6, "md": 3, "lg": 3},
                                    ),
                                    # Contact Developer
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.EMAIL_OUTLINED, size=responsive["icon_size"] + 4, color="#4CAF50"),
                                                width=50,
                                                height=50,
                                                bgcolor=ft.Colors.with_opacity(0.1, "#4CAF50"),
                                                border_radius=12,
                                                alignment=ft.alignment.center,
                                            ),
                                            ft.Container(height=8),
                                            ft.Text("Contact Developer", size=responsive["font_body"], color=theme["text_primary"], weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER),
                                            ft.Text("Send feedback or suggestions", size=max(9, responsive["font_body"] - 3), color=theme["text_hint"], text_align=ft.TextAlign.CENTER),
                                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                                        padding=ft.padding.all(responsive["button_padding"]),
                                        border_radius=12,
                                        bgcolor=theme["bg_secondary"],
                                        on_click=show_contact_developer_dialog,
                                        ink=True,
                                        alignment=ft.alignment.center,
                                        col={"xs": 6, "sm": 6, "md": 3, "lg": 3},
                                    ),
                                    # Terms of Service
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=responsive["icon_size"] + 4, color="#FF9800"),
                                                width=50,
                                                height=50,
                                                bgcolor=ft.Colors.with_opacity(0.1, "#FF9800"),
                                                border_radius=12,
                                                alignment=ft.alignment.center,
                                            ),
                                            ft.Container(height=8),
                                            ft.Text("Terms of Service", size=responsive["font_body"], color=theme["text_primary"], weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER),
                                            ft.Text("Read our terms and conditions", size=max(9, responsive["font_body"] - 3), color=theme["text_hint"], text_align=ft.TextAlign.CENTER),
                                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                                        padding=ft.padding.all(responsive["button_padding"]),
                                        border_radius=12,
                                        bgcolor=theme["bg_secondary"],
                                        on_click=show_terms_dialog,
                                        ink=True,
                                        alignment=ft.alignment.center,
                                        col={"xs": 6, "sm": 6, "md": 3, "lg": 3},
                                    ),
                                    # Privacy Policy
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.PRIVACY_TIP_OUTLINED, size=responsive["icon_size"] + 4, color="#9C27B0"),
                                                width=50,
                                                height=50,
                                                bgcolor=ft.Colors.with_opacity(0.1, "#9C27B0"),
                                                border_radius=12,
                                                alignment=ft.alignment.center,
                                            ),
                                            ft.Container(height=8),
                                            ft.Text("Privacy Policy", size=responsive["font_body"], color=theme["text_primary"], weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER),
                                            ft.Text("Learn how we protect your data", size=max(9, responsive["font_body"] - 3), color=theme["text_hint"], text_align=ft.TextAlign.CENTER),
                                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                                        padding=ft.padding.all(responsive["button_padding"]),
                                        border_radius=12,
                                        bgcolor=theme["bg_secondary"],
                                        on_click=show_privacy_dialog,
                                        ink=True,
                                        alignment=ft.alignment.center,
                                        col={"xs": 6, "sm": 6, "md": 3, "lg": 3},
                                    ),
                                ], spacing=responsive["section_spacing"], run_spacing=responsive["section_spacing"], alignment=ft.MainAxisAlignment.CENTER),
                                padding=ft.padding.symmetric(horizontal=responsive["padding"], vertical=responsive["section_spacing"]),
                            ),
                            ft.Container(height=responsive["section_spacing"]),
                        ]),
                        visible=False,
                    ),
                ]),
                bgcolor=theme["bg_card"], border_radius=12,
                border=ft.border.all(1, theme["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            ),
            
            ft.Container(height=responsive["padding"]),
            
            # ==================== LOGOUT ====================
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.LOGOUT, size=responsive["icon_size"] - 2, color=theme["error"]),
                    ft.Text("Logout", size=responsive["font_body"], color=theme["error"], weight=ft.FontWeight.W_500),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=theme["bg_card"], padding=ft.padding.symmetric(horizontal=responsive["padding"], vertical=responsive["button_padding"]),
                border_radius=12, on_click=show_logout_dialog,
                border=ft.border.all(1, theme["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
                ink=True,
            ),
            
            ft.Container(height=responsive["section_spacing"]),
            
            # ==================== DELETE ACCOUNT ====================
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DELETE_FOREVER, size=responsive["icon_size"] - 2, color=theme["text_hint"]),
                    ft.Text("Delete Account", size=responsive["font_body"], color=theme["text_hint"], weight=ft.FontWeight.W_500),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor="transparent", padding=ft.padding.symmetric(horizontal=responsive["padding"], vertical=responsive["button_padding"]),
                border_radius=12, on_click=lambda e: show_delete_account_dialog(),
                border=ft.border.all(1, theme["border"]),
                ink=True,
            ),
            
            ft.Container(height=20),
        ], spacing=0, scroll=ft.ScrollMode.AUTO)
        
        return settings_content, responsive
    
    # Initial build
    content, responsive = build_settings_content()
    
    # Wrap in responsive container with max-width for larger screens
    # Use width constraint when max_width is set, otherwise expand
    inner_container = ft.Container(
        content=content,
        expand=True if responsive["max_width"] is None else False,
        width=responsive["max_width"],
        padding=ft.padding.symmetric(horizontal=responsive["padding"], vertical=12),
    )
    
    return ft.Container(
        content=ft.Row(
            [inner_container],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        ),
        bgcolor=c["bg_primary"],
        expand=True,
    )


def ProfilePage(page: ft.Page, user: dict, on_back=None):
    """Standalone profile page - Responsive"""
    from utils.theme import get_theme
    c = get_theme(page)
    initials = get_initials(user.get('first_name', ''), user.get('last_name', ''))
    
    # Responsive values
    width = page.width or 400
    if width < 480:  # Small mobile
        profile_size = 80
        font_title = 16
        font_body = 12
        padding = 16
        max_width = None
        icon_size = 20
    elif width < 600:  # Mobile
        profile_size = 90
        font_title = 18
        font_body = 13
        padding = 20
        max_width = None
        icon_size = 22
    elif width < 900:  # Tablet
        profile_size = 110
        font_title = 20
        font_body = 14
        padding = 28
        max_width = 500
        icon_size = 24
    else:  # Desktop
        profile_size = 120
        font_title = 22
        font_body = 15
        padding = 32
        max_width = 600
        icon_size = 24
    
    user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
    
    profile_content = ft.Column([
        ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=c["text_primary"], icon_size=icon_size, on_click=lambda e: on_back() if on_back else None),
                ft.Text("Profile", size=font_title, weight=ft.FontWeight.W_600, color=c["text_primary"]),
            ], spacing=8),
        ),
        ft.Container(height=padding),
        ft.Container(
            content=ft.Text(initials, size=profile_size * 0.4, weight=ft.FontWeight.W_600, color="#ffffff"),
            width=profile_size, height=profile_size, bgcolor=c["accent"], border_radius=profile_size / 2, alignment=ft.alignment.center,
        ),
        ft.Container(height=8),
        ft.Text(user_name, size=font_title, weight=ft.FontWeight.W_600, color=c["text_primary"]),
        ft.Text(user.get('email', ''), size=font_body, color=c["text_secondary"]),
        ft.Text(user.get('student_id', ''), size=font_body - 1, color=c["text_hint"]),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
    
    # Use width constraint when max_width is set, otherwise expand
    inner_container = ft.Container(
        content=profile_content,
        expand=True if max_width is None else False,
        width=max_width,
        padding=padding,
    )
    
    return ft.Container(
        content=ft.Row(
            [inner_container],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        ),
        bgcolor=c["bg_primary"],
        expand=True,
    )
