"""
SpottEd Login Page - CSPC Classroom Management System
Fully Responsive Layout
"""
import asyncio
import flet as ft
from database import db
from utils.theme import get_theme


def LoginPage(page: ft.Page, on_login=None, on_register=None, on_forgot_password=None):
    """Login page - Fully Responsive for Mobile, Tablet, Desktop"""
    
    def t():
        return get_theme(page)
    
    # Form state
    email_field = ft.Ref[ft.TextField]()
    password_field = ft.Ref[ft.TextField]()
    remember_me = ft.Ref[ft.Checkbox]()
    error_text = ft.Ref[ft.Text]()
    login_btn = ft.Ref[ft.ElevatedButton]()
    google_btn = ft.Ref[ft.OutlinedButton]()
    
    def show_error(message: str):
        error_text.current.value = message
        error_text.current.visible = True
        page.update()
    
    def hide_error():
        error_text.current.visible = False
        page.update()
    
    def handle_login(e):
        hide_error()
        
        email = email_field.current.value.strip()
        password = password_field.current.value
        
        if not email:
            show_error("Please enter your CSPC email address")
            return
        
        if not password:
            show_error("Please enter your password")
            return
        
        login_btn.current.disabled = True
        login_btn.current.content.controls[1].value = "Signing in..."
        page.update()
        
        student_id = email.split('@')[0] if '@' in email else email
        user = db.authenticate_user(student_id, password)
        
        if not user:
            user_data = db.get_user_by_email(email)
            if user_data:
                user = db.authenticate_user(user_data['student_id'], password)
        
        if user:
            if on_login:
                on_login(user)
        else:
            show_error("Invalid email or password")
            login_btn.current.disabled = False
            login_btn.current.content.controls[1].value = "Sign In"
            page.update()
    
    def handle_register(e):
        if on_register:
            on_register()

    def _responsive_form_width() -> float:
        w_win = getattr(getattr(page, "window", None), "width", None)
        pw = getattr(page, "width", None) or getattr(page, "window_width", None)
        base = float(w_win or pw or 400)
        return max(260.0, min(480.0, base - 48.0))

    def _blocked_google_login():
        """Runs in executor thread — Google browser flow + DB lookup."""
        from services.google_oauth_service import fetch_google_profile
        profile = fetch_google_profile()
        return db.sign_in_with_google(
            profile.sub,
            profile.email,
            profile.given_name,
            profile.family_name,
            profile.picture,
            verified_email=profile.verified_email,
        )

    async def handle_google_login(_):
        hide_error()
        from services.google_oauth_service import (
            GoogleOAuthConfigurationError,
            GoogleOAuthFlowError,
            google_oauth_configured,
        )

        if not google_oauth_configured():
            show_error(
                "Add real GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env.local "
                "(see file comments). Placeholders cannot authenticate."
            )
            return

        google_btn.current.disabled = True
        txt = google_btn.current.content.controls[1]
        if hasattr(txt, "value"):
            prev = txt.value
            txt.value = "Opening browser…"
        else:
            prev = None
        page.update()

        try:
            user = await asyncio.to_thread(_blocked_google_login)
            if user and on_login:
                on_login(user)
            elif not user:
                show_error(
                    "Google sign-in could not complete — use a verified Google account "
                    "or sign in with your CSPC email and password."
                )
        except GoogleOAuthConfigurationError as ex:
            show_error(str(ex))
        except GoogleOAuthFlowError as ex:
            show_error(str(ex))
        except Exception:
            show_error(
                "Google sign-in failed. Check credentials, redirect URIs in Google Console, "
                "and network access, then try again."
            )
        finally:
            google_btn.current.disabled = False
            if hasattr(txt, "value"):
                txt.value = prev or "Sign in with Google"
            page.update()
    
    def show_reset_dialog(e):
        reset_email = ft.Ref[ft.TextField]()
        c = t()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def send_code(e):
            email = reset_email.current.value.strip()
            if not email:
                return
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Demo: Reset code is 123456"),
                bgcolor=c["success"], duration=5000,
            )
            page.snack_bar.open = True
            dialog.open = False
            page.update()
            if on_forgot_password:
                on_forgot_password()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.KEY, color="#FFC107", size=24),
                            ft.Text(
                                "Reset Password",
                                size=18,
                                weight=ft.FontWeight.W_600,
                                color=c["text_primary"],
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=c["text_secondary"],
                        icon_size=20,
                        on_click=close_dialog,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Enter your CSPC email address to receive a verification code.",
                            size=13,
                            color=c["text_secondary"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=16),
                        ft.Icon(ft.Icons.MAIL_OUTLINE, size=48, color=c["accent"]),
                        ft.Container(height=16),
                        ft.Text("CSPC Email Address", size=12, color=c["text_secondary"]),
                        ft.TextField(
                            ref=reset_email,
                            hint_text="your.email@my.cspc.edu.ph",
                            prefix_icon=ft.Icons.MAIL_OUTLINE,
                            border_color=c["border"],
                            focused_border_color=c["accent"],
                            hint_style=ft.TextStyle(color=c["text_hint"]),
                            text_style=ft.TextStyle(color=c["text_primary"]),
                            cursor_color=c["accent"],
                            border_radius=8,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Demo Note:",
                                        size=11,
                                        weight=ft.FontWeight.W_600,
                                        color="#FFC107",
                                    ),
                                    ft.Text(
                                        "Code will be shown in notification.",
                                        size=11,
                                        color=c["text_secondary"],
                                    ),
                                ],
                                spacing=2,
                            ),
                            bgcolor=c["accent_bg"],
                            padding=12,
                            border_radius=8,
                            margin=ft.margin.only(top=8),
                        ),
                    ],
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=min(page.width * 0.9 if page.width else 360, 420),
            ),
            actions=[
                ft.ElevatedButton(
                    "Cancel",
                    bgcolor=c["bg_secondary"],
                    color=c["text_primary"],
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=close_dialog,
                ),
                ft.ElevatedButton(
                    content=ft.Row(
                        [ft.Icon(ft.Icons.MAIL, size=18), ft.Text("Send Code")],
                        spacing=6,
                    ),
                    bgcolor=c["accent"],
                    color="#ffffff",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=send_code,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["bg_card"],
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_it_support_dialog(e):
        c = t()

        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def submit_request(e):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Support request submitted! We'll respond within 24 hours."),
                bgcolor=c["success"],
            )
            page.snack_bar.open = True
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Text(
                        "IT Support Request",
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color=c["text_primary"],
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
                        ft.Text(
                            "Fill out the form below and our support team will get back to you within 24 hours.",
                            size=13,
                            color=c["text_secondary"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=12),
                        ft.Text("Full Name", size=12, color=c["text_secondary"]),
                        ft.TextField(
                            hint_text="Enter your full name",
                            border_color=c["border"],
                            focused_border_color=c["accent"],
                            hint_style=ft.TextStyle(color=c["text_hint"]),
                            text_style=ft.TextStyle(color=c["text_primary"]),
                            cursor_color=c["accent"],
                            border_radius=8,
                        ),
                        ft.Text("Email Address", size=12, color=c["text_secondary"]),
                        ft.TextField(
                            hint_text="your.email@my.cspc.edu.ph",
                            border_color=c["border"],
                            focused_border_color=c["accent"],
                            hint_style=ft.TextStyle(color=c["text_hint"]),
                            text_style=ft.TextStyle(color=c["text_primary"]),
                            cursor_color=c["accent"],
                            border_radius=8,
                        ),
                        ft.Text("Issue Category", size=12, color=c["text_secondary"]),
                        ft.Dropdown(
                            value="Login Issues",
                            options=[
                                ft.dropdown.Option("Login Issues"),
                                ft.dropdown.Option("Account Recovery"),
                                ft.dropdown.Option("Technical Problems"),
                                ft.dropdown.Option("Other"),
                            ],
                            border_color=c["border"],
                            focused_border_color=c["accent"],
                            text_style=ft.TextStyle(color=c["text_primary"]),
                            border_radius=8,
                        ),
                        ft.Text("Message", size=12, color=c["text_secondary"]),
                        ft.TextField(
                            hint_text="Describe your issue...",
                            multiline=True,
                            min_lines=3,
                            max_lines=5,
                            border_color=c["border"],
                            focused_border_color=c["accent"],
                            hint_style=ft.TextStyle(color=c["text_hint"]),
                            text_style=ft.TextStyle(color=c["text_primary"]),
                            cursor_color=c["accent"],
                            border_radius=8,
                        ),
                    ],
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=min(page.width * 0.9 if page.width else 320, 320),
            ),
            actions=[
                ft.ElevatedButton(
                    "Cancel",
                    bgcolor=c["bg_secondary"],
                    color=c["text_primary"],
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=close_dialog,
                ),
                ft.ElevatedButton(
                    "Submit",
                    bgcolor=c["accent"],
                    color="#ffffff",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=submit_request,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["bg_card"],
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # Build responsive content
    def build_content():
        c = t()
        form_w = _responsive_form_width()
        divider_row = ft.Row(
            [
                ft.Container(
                    expand=True,
                    content=ft.Divider(color=c["border"], height=1, thickness=1),
                    alignment=ft.alignment.center,
                ),
                ft.Padding(
                    padding=ft.padding.symmetric(horizontal=10),
                    content=ft.Text("or", size=12, color=c["text_hint"]),
                ),
                ft.Container(
                    expand=True,
                    content=ft.Divider(color=c["border"], height=1, thickness=1),
                    alignment=ft.alignment.center,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=c["text_primary"]),
                    ft.Column([
                        ft.Text("Welcome Back", size=22, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                        ft.Text("Sign in to your CSPC account", size=13, color=c["text_secondary"]),
                    ], spacing=2),
                ], spacing=8),
                margin=ft.margin.only(bottom=20),
            ),
            
            # CCS Logo Card
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Image(
                            src="logo.png",
                            width=90,
                            height=90,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        width=90,
                        height=90,
                        border_radius=20,
                        alignment=ft.alignment.center,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    ft.Text("CCS", size=28, weight=ft.FontWeight.W_800, color=c["accent"]),
                    ft.Text("Camarines Sur Polytechnic Colleges", size=13, color=c["text_secondary"],
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("Classroom Management Locator", size=11, color=c["text_hint"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                bgcolor=c["bg_card"], padding=28, border_radius=16,
            ),
            
            ft.Container(height=14),
            
            # Demo Credentials
            ft.Container(
                content=ft.Column([
                    ft.Text("Demo Credentials:", size=13, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                    ft.Container(height=8),
                    ft.Row([ft.Text("Student:", size=12, color=c["text_secondary"], width=80),
                            ft.Text("studentemail@my.cspc.edu.ph", size=12, color="#4CAF50", 
                                    overflow=ft.TextOverflow.ELLIPSIS, expand=True)], spacing=4),
                    ft.Row([ft.Text("Student ID:", size=12, color=c["text_secondary"], width=80),
                            ft.Text("2*********", size=12, color="#4CAF50")], spacing=4),
                    ft.Row([ft.Text("Instructor:", size=12, color=c["text_secondary"], width=80),
                            ft.Text("instructor@my.cspc.edu.ph", size=12, color="#4CAF50",
                                    overflow=ft.TextOverflow.ELLIPSIS, expand=True)], spacing=4),
                    ft.Row([ft.Text("Admin:", size=12, color=c["text_secondary"], width=80),
                            ft.Text("admin@my.cspc.edu.ph", size=12, color="#4CAF50",
                                    overflow=ft.TextOverflow.ELLIPSIS, expand=True)], spacing=4),
                ], spacing=4),
                bgcolor=c["bg_secondary"], border=ft.border.all(1, c["border"]),
                padding=16, border_radius=12,
            ),
            
            ft.Container(height=14),
            
            # Error message
            ft.Text("", ref=error_text, size=13, color=c["error"], visible=False,
                    text_align=ft.TextAlign.CENTER),
            
            # Login form
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        width=form_w,
                        content=ft.Row(
                            [
                                ft.OutlinedButton(
                                    ref=google_btn,
                                    expand=True,
                                    height=48,
                                    content=ft.Row(
                                        [
                                            ft.Image(
                                                src="google_g_logo.svg",
                                                width=20,
                                                height=20,
                                                fit=ft.ImageFit.CONTAIN,
                                            ),
                                            ft.Text(
                                                "Sign in with Google",
                                                size=14,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=12,
                                        tight=True,
                                    ),
                                    style=ft.ButtonStyle(
                                        color="#3c4043",
                                        bgcolor={
                                            ft.ControlState.DEFAULT: "#ffffff",
                                            ft.ControlState.DISABLED: "#f5f5f5",
                                            ft.ControlState.HOVERED: "#f8fafc",
                                        },
                                        overlay_color={ft.ControlState.HOVERED: "#1f000000"},
                                        side={
                                            ft.ControlState.DEFAULT: ft.BorderSide(1, "#dadce0"),
                                            ft.ControlState.HOVERED: ft.BorderSide(1, "#c6cacf"),
                                            ft.ControlState.DISABLED: ft.BorderSide(1, "#e8eaed"),
                                        },
                                        elevation={ft.ControlState.DEFAULT: 2, ft.ControlState.HOVERED: 5},
                                        animation_duration=200,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                        text_style=ft.TextStyle(weight=ft.FontWeight.W_600),
                                    ),
                                    on_click=lambda _: page.run_task(handle_google_login),
                                ),
                            ],
                            spacing=0,
                            tight=True,
                        ),
                    ),
                    ft.Container(height=10),
                    divider_row,
                    ft.Container(height=12),
                    ft.Text(
                        "Sign in with your CSPC email",
                        size=11,
                        color=c["text_hint"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.Text("CSPC Email Address", size=12, color=c["text_secondary"]),
                    ft.TextField(
                        ref=email_field, hint_text="your.name@my.cspc.edu.ph",
                        prefix_icon=ft.Icons.PERSON_OUTLINE, border_color=c["border"],
                        focused_border_color=c["accent"], hint_style=ft.TextStyle(color=c["text_hint"]),
                        text_style=ft.TextStyle(color=c["text_primary"]), cursor_color=c["accent"], border_radius=10,
                    ),
                    ft.Container(height=10),
                    ft.Text("Password", size=12, color=c["text_secondary"]),
                    ft.TextField(
                        ref=password_field, hint_text="Enter your password",
                        prefix_icon=ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True,
                        border_color=c["border"], focused_border_color=c["accent"],
                        hint_style=ft.TextStyle(color=c["text_hint"]), text_style=ft.TextStyle(color=c["text_primary"]),
                        cursor_color=c["accent"], border_radius=10, on_submit=handle_login,
                    ),
                    ft.Container(height=6),
                    ft.Row([
                        ft.Row([
                            ft.Checkbox(ref=remember_me, value=False, check_color="#ffffff",
                                        fill_color={ft.ControlState.SELECTED: c["accent"],
                                                    ft.ControlState.DEFAULT: c["border"]}, scale=0.85),
                            ft.Text("Remember me", size=12, color=c["text_secondary"]),
                        ], spacing=0),
                        ft.TextButton(content=ft.Text("Forgot password?", size=12, color=c["accent"]),
                                      on_click=show_reset_dialog),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
                    ft.Container(height=14),
                    ft.Container(
                        width=form_w,
                        content=ft.Row(
                            [
                                ft.ElevatedButton(
                                    ref=login_btn,
                                    expand=True,
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.LOGIN, size=20),
                                        ft.Text("Sign In", size=15, weight=ft.FontWeight.W_600),
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                                    bgcolor=c["accent"], color="#ffffff", height=50,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                    on_click=handle_login,
                                ),
                            ],
                            spacing=0,
                            tight=True,
                        ),
                    ),
                ], spacing=4),
                bgcolor=c["bg_card"], padding=20, border_radius=12,
            ),
            
            ft.Container(height=18),
            
            # Register link
            ft.Column([
                ft.Row([
                    ft.Text("Don't have an account?", size=13, color=c["text_secondary"]),
                    ft.TextButton(content=ft.Text("Create Account", size=13, weight=ft.FontWeight.W_600,
                                                   color=c["accent"]), on_click=handle_register),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2, wrap=True),
                ft.Text("Only CSPC students, faculty, and staff can create accounts",
                        size=10, color=c["text_hint"], text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            
            ft.Container(height=10),
            
            # IT Support button
            ft.Row([
                ft.Text("Need help? Contact", size=13, color=c["text_secondary"]),
                ft.TextButton(content=ft.Text("IT Support", size=13, weight=ft.FontWeight.W_600,
                                               color=c["accent"]), on_click=show_it_support_dialog),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=2, wrap=True),
            
            ft.Container(height=16),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
    
    # Main responsive container
    return ft.Container(
        content=ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=build_content(),
                    col={"xs": 12, "sm": 11, "md": 7, "lg": 5, "xl": 4},
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=t()["bg_primary"],
        expand=True,
        padding=ft.padding.symmetric(vertical=12),
    )
