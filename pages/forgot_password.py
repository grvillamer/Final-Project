"""
SpottEd Forgot Password Page - CSPC Classroom Management System
Responsive Layout with Email Recovery
"""
import flet as ft
import random
from database import db
from utils.helpers import validate_email
from utils.theme import get_theme
from config import config


def ForgotPasswordPage(page: ft.Page, on_back=None):
    """Forgot password / password reset page - Responsive with email recovery"""
    
    # Theme
    def t():
        return get_theme(page)
    
    c = t()
    
    # Form state
    email_field = ft.Ref[ft.TextField]()
    code_field = ft.Ref[ft.TextField]()
    new_password_field = ft.Ref[ft.TextField]()
    confirm_password_field = ft.Ref[ft.TextField]()
    error_text = ft.Ref[ft.Text]()
    success_text = ft.Ref[ft.Text]()
    action_btn = ft.Ref[ft.ElevatedButton]()
    step_indicators = ft.Ref[ft.Row]()
    email_section = ft.Ref[ft.Container]()
    code_section = ft.Ref[ft.Container]()
    password_section = ft.Ref[ft.Container]()
    email_display = ft.Ref[ft.Text]()
    
    # Generate random 6-digit code
    def generate_code():
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    state = {"step": 1, "user": None, "verification_code": generate_code(), "email": ""}
    
    def show_error(message: str):
        error_text.current.value = message
        error_text.current.visible = True
        success_text.current.visible = False
        page.update()
    
    def show_success(message: str):
        success_text.current.value = message
        success_text.current.visible = True
        error_text.current.visible = False
        page.update()
    
    def hide_messages():
        error_text.current.visible = False
        success_text.current.visible = False
        page.update()
    
    def update_step_indicators(step: int):
        """Update the visual step indicators"""
        for i, indicator in enumerate(step_indicators.current.controls):
            if isinstance(indicator, ft.Container) and hasattr(indicator, 'content'):
                if hasattr(indicator.content, 'value'):  # It's a text container (step number)
                    step_num = i // 2 + 1  # Account for dividers
                    if step_num <= step:
                        indicator.bgcolor = "#4CAF50"
                        indicator.content.color = "#ffffff"
                    else:
                        indicator.bgcolor = c["border"]
                        indicator.content.color = c["text_secondary"]
                elif indicator.height == 2:  # It's a divider
                    divider_after_step = (i // 2)
                    if divider_after_step < step:
                        indicator.bgcolor = "#4CAF50"
                    else:
                        indicator.bgcolor = c["border"]
        page.update()
    
    def _mask_email(email: str) -> str:
        """Mask email for display (e.g., gv***er@my.cspc.edu.ph)."""
        parts = email.split('@')
        if len(parts) == 2:
            username = parts[0]
            domain = parts[1]
            if len(username) > 3:
                masked = username[:2] + '*' * (len(username) - 4) + username[-2:] + '@' + domain
            else:
                masked = username[0] + '*' * (len(username) - 1) + '@' + domain
        else:
            masked = email
        
        return masked

    def _send_verification_email(email: str, code: str) -> tuple[bool, str]:
        """
        Try to send the verification code via SMTP.
        Returns (success, error_message).
        """
        if not config.SMTP_ENABLED or not config.SMTP_HOST or not config.SMTP_FROM_EMAIL:
            return False, "Email sending not configured"
        
        try:
            from email.message import EmailMessage
            import smtplib
            
            msg = EmailMessage()
            msg["Subject"] = "Your CSPC password reset code"
            msg["From"] = f"{config.SMTP_FROM_NAME} <{config.SMTP_FROM_EMAIL}>"
            msg["To"] = email
            msg.set_content(
                f"Hi,\n\n"
                f"Here is your CSPC password reset verification code: {code}\n\n"
                f"This code is valid for 10 minutes. If you did not request a password reset, "
                f"you can safely ignore this email.\n\n"
                f"{config.APP_NAME}"
            )
            
            if config.SMTP_USE_TLS:
                with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
                    server.starttls()
                    if config.SMTP_USERNAME:
                        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                    server.send_message(msg)
            else:
                with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT) as server:
                    if config.SMTP_USERNAME:
                        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                    server.send_message(msg)
            
            return True, ""
        except Exception as exc:
            print(f"[FORGOT_PASSWORD] Failed to send verification email: {exc}")
            return False, str(exc)
    
    def handle_send_code(e):
        hide_messages()
        
        email = email_field.current.value.strip()
        
        if not email:
            show_error("Please enter your CSPC email address")
            return
        
        if not validate_email(email):
            show_error("Please enter a valid email address")
            return
        
        # Check if it's a CSPC email (for production)
        # if not email.lower().endswith('@my.cspc.edu.ph') and not email.lower().endswith('@cspc.edu.ph'):
        #     show_error("Please use your CSPC email address")
        #     return
        
        # Find user by email
        user = db.get_user_by_email(email)
        
        if user:
            state["user"] = user
            state["email"] = email
            state["verification_code"] = generate_code()  # Generate new code
            state["step"] = 2
            
            # Try to send verification email (falls back to demo notification if not configured)
            masked_email = _mask_email(email)
            email_sent, error_msg = _send_verification_email(email, state["verification_code"])
            
            # Update UI
            email_section.current.visible = False
            code_section.current.visible = True
            email_display.current.value = email
            update_step_indicators(2)
            
            action_btn.current.content.controls[0].name = ft.Icons.VERIFIED_USER
            action_btn.current.content.controls[1].value = "Verify Code"
            
            # Notification
            if email_sent:
                # Real email: don't show the code in UI
                page.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.EMAIL, color="#ffffff", size=20),
                        ft.Column([
                            ft.Text("Verification code sent!", weight=ft.FontWeight.W_600, color="#ffffff"),
                            ft.Text("Please check your CSPC email to continue.", size=12, color="#ffffff"),
                        ], spacing=0, expand=True),
                    ], spacing=12),
                    bgcolor="#4CAF50",
                    duration=8000,
                )
                page.snack_bar.open = True
            else:
                # Demo/dev mode: still show code for convenience
                page.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.EMAIL, color="#ffffff", size=20),
                        ft.Column([
                            ft.Text("Demo: verification code generated", weight=ft.FontWeight.W_600, color="#ffffff"),
                            ft.Text(f"Code: {state['verification_code']} (no email configured)", size=12, color="#ffffff"),
                        ], spacing=0, expand=True),
                    ], spacing=12),
                    bgcolor="#4CAF50",
                    duration=10000,
                )
                page.snack_bar.open = True
            
            show_success(f"Verification code sent to {masked_email}")
        else:
            show_error("No account found with this email address")
        
        page.update()
    
    def handle_verify_code(e):
        hide_messages()
        
        code = code_field.current.value.strip()
        
        if not code:
            show_error("Please enter the verification code")
            return
        
        if len(code) != 6:
            show_error("Please enter the 6-digit code")
            return
        
        if code != state["verification_code"]:
            show_error("Invalid verification code. Please try again.")
            return
        
        state["step"] = 3
        
        # Update UI
        code_section.current.visible = False
        password_section.current.visible = True
        update_step_indicators(3)
        
        action_btn.current.content.controls[0].name = ft.Icons.LOCK_RESET
        action_btn.current.content.controls[1].value = "Reset Password"
        
        show_success("Code verified! Create your new password.")
        page.update()
    
    def handle_reset_password(e):
        hide_messages()
        
        new_password = new_password_field.current.value
        confirm_password = confirm_password_field.current.value
        
        if not new_password:
            show_error("Please enter a new password")
            return
        
        if len(new_password) < 8:
            show_error("Password must be at least 8 characters")
            return
        
        if not any(c.isdigit() for c in new_password):
            show_error("Password must contain at least one number")
            return
        
        if new_password != confirm_password:
            show_error("Passwords do not match")
            return
        
        # Update password
        success, error_msg = db.update_password(state["user"]["id"], new_password)
        
        if success:
            action_btn.current.disabled = True
            action_btn.current.content.controls[0].name = ft.Icons.CHECK_CIRCLE
            action_btn.current.content.controls[1].value = "Password Reset!"
            action_btn.current.bgcolor = c["border"]
            
            # Show success and redirect
            def on_snackbar_dismiss(e):
                if on_back:
                    on_back()
            
            page.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#ffffff", size=20),
                    ft.Text("Password reset successfully!", color="#ffffff"),
                ], spacing=12),
                bgcolor="#4CAF50",
                duration=2000,
                on_dismiss=on_snackbar_dismiss,
            )
            page.snack_bar.open = True
            page.update()
        else:
            show_error(error_msg or "Failed to reset password. Please try again.")
    
    def handle_action(e):
        if state["step"] == 1:
            handle_send_code(e)
        elif state["step"] == 2:
            handle_verify_code(e)
        elif state["step"] == 3:
            handle_reset_password(e)
    
    def handle_back(e):
        if state["step"] > 1:
            # Go back one step
            if state["step"] == 2:
                state["step"] = 1
                email_section.current.visible = True
                code_section.current.visible = False
                email_field.current.disabled = False
                action_btn.current.content.controls[0].name = ft.Icons.SEND
                action_btn.current.content.controls[1].value = "Send Code"
                update_step_indicators(1)
            elif state["step"] == 3:
                state["step"] = 2
                password_section.current.visible = False
                code_section.current.visible = True
                action_btn.current.content.controls[0].name = ft.Icons.VERIFIED_USER
                action_btn.current.content.controls[1].value = "Verify Code"
                update_step_indicators(2)
            hide_messages()
            page.update()
        else:
            if on_back:
                on_back()
    
    def resend_code(e):
        state["verification_code"] = generate_code()  # Generate new code
        email = state.get("email")
        
        if email:
            masked_email = _mask_email(email)
            email_sent, error_msg = _send_verification_email(email, state["verification_code"])
            
            if email_sent:
                page.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.REFRESH, color="#ffffff", size=20),
                        ft.Column([
                            ft.Text("New code sent!", weight=ft.FontWeight.W_600, color="#ffffff"),
                            ft.Text(f"Please check {masked_email} for the latest code.", size=12, color="#ffffff"),
                        ], spacing=0, expand=True),
                    ], spacing=12),
                    bgcolor="#4CAF50",
                    duration=8000,
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.REFRESH, color="#ffffff", size=20),
                        ft.Column([
                            ft.Text("Demo: new code generated", weight=ft.FontWeight.W_600, color="#ffffff"),
                            ft.Text(f"Code: {state['verification_code']} (no email configured)", size=12, color="#ffffff"),
                        ], spacing=0, expand=True),
                    ], spacing=12),
                    bgcolor="#4CAF50",
                    duration=8000,
                )
        else:
            # No email on record (shouldn't normally happen once step 1 is complete)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Unable to resend code: email address not available.", color="#ffffff"),
                bgcolor="#F44336",
                duration=5000,
            )
        
        page.snack_bar.open = True
        page.update()
    
    # Build step indicator
    def build_step(num: int, active: bool = False):
        return ft.Container(
            content=ft.Text(str(num), size=12, color="#ffffff" if active else c["text_secondary"],
                           weight=ft.FontWeight.W_600),
            width=32, height=32,
            bgcolor="#4CAF50" if active else c["border"],
            border_radius=16,
            alignment=ft.alignment.center,
        )
    
    def build_divider(active: bool = False):
        return ft.Container(width=50, height=2, bgcolor="#4CAF50" if active else c["border"])
    
    # Responsive content with centered card
    content_card = ft.Container(
        content=ft.Column([
            # Icon
            ft.Container(
                content=ft.Icon(ft.Icons.KEY, size=40, color="#FFC107"),
                width=80, height=80, bgcolor="#1a3d2e", border_radius=40,
                alignment=ft.alignment.center,
            ),
            
            ft.Text("Account Recovery", size=22, weight=ft.FontWeight.W_700, color=c["text_primary"]),
            ft.Text("Enter your CSPC email address and we'll send you a verification code.",
                   size=13, color=c["text_secondary"], text_align=ft.TextAlign.CENTER),
            
            ft.Container(height=16),
            
            # Messages
            ft.Text("", ref=error_text, size=12, color="#F44336", visible=False, text_align=ft.TextAlign.CENTER),
            ft.Text("", ref=success_text, size=12, color="#4CAF50", visible=False, text_align=ft.TextAlign.CENTER),
            
            # Step indicators
            ft.Row(
                ref=step_indicators,
                controls=[
                    build_step(1, True),
                    build_divider(False),
                    build_step(2, False),
                    build_divider(False),
                    build_step(3, False),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            
            ft.Container(height=20),
            
            # ==================== STEP 1: Email ====================
            ft.Container(
                ref=email_section,
                content=ft.Column([
                    ft.Text("CSPC Email Address", size=12, color=c["text_secondary"]),
                    ft.TextField(
                        ref=email_field,
                        hint_text="your.email@my.cspc.edu.ph",
                        prefix_icon=ft.Icons.EMAIL_OUTLINED,
                        keyboard_type=ft.KeyboardType.EMAIL,
                        border_color=c["border"], focused_border_color="#4CAF50",
                        hint_style=ft.TextStyle(color=c["text_hint"]),
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        cursor_color="#4CAF50", border_radius=10,
                        on_submit=handle_action,
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=c["text_secondary"]),
                            ft.Text("We'll send a 6-digit verification code to this email",
                                   size=11, color=c["text_secondary"]),
                        ], spacing=6),
                        margin=ft.margin.only(top=8),
                    ),
                ], spacing=6),
                visible=True,
            ),
            
            # ==================== STEP 2: Verification Code ====================
            ft.Container(
                ref=code_section,
                content=ft.Column([
                    # Email display
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.EMAIL, size=18, color="#4CAF50"),
                            ft.Text("", ref=email_display, size=13, color=c["text_primary"]),
                            ft.TextButton(
                                content=ft.Text("Change", size=11, color="#4CAF50"),
                                on_click=lambda e: (
                                    setattr(email_section.current, 'visible', True),
                                    setattr(code_section.current, 'visible', False),
                                    setattr(state, '__setitem__', ('step', 1)),
                                    update_step_indicators(1),
                                    page.update()
                                ),
                            ),
                        ], spacing=8),
                        bgcolor=c["accent_bg"], padding=12, border_radius=8,
                        margin=ft.margin.only(bottom=16),
                    ),
                    
                    ft.Text("Verification Code", size=12, color=c["text_secondary"]),
                    ft.TextField(
                        ref=code_field,
                        hint_text="Enter 6-digit code",
                        prefix_icon=ft.Icons.PIN_OUTLINED,
                        keyboard_type=ft.KeyboardType.NUMBER,
                        border_color=c["border"], focused_border_color="#4CAF50",
                        hint_style=ft.TextStyle(color=c["text_hint"]),
                        text_style=ft.TextStyle(color=c["text_primary"], size=18, weight=ft.FontWeight.W_600),
                        cursor_color="#4CAF50", border_radius=10,
                        text_align=ft.TextAlign.CENTER,
                        max_length=6,
                        on_submit=handle_action,
                    ),
                    
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Didn't receive code?", size=12, color=c["text_secondary"]),
                            ft.TextButton(
                                content=ft.Text("Resend", size=12, color="#4CAF50", weight=ft.FontWeight.W_600),
                                on_click=resend_code,
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        margin=ft.margin.only(top=8),
                    ),
                    
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.TIMER_OUTLINED, size=14, color=c["text_hint"]),
                            ft.Text("Code expires in 10 minutes", size=11, color=c["text_hint"]),
                        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                    ),
                ], spacing=6),
                visible=False,
            ),
            
            # ==================== STEP 3: New Password ====================
            ft.Container(
                ref=password_section,
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color="#4CAF50"),
                            ft.Text("Email verified successfully!", size=13, color="#4CAF50",
                                   weight=ft.FontWeight.W_500),
                        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                        bgcolor=c["accent_bg"], padding=12, border_radius=8,
                        margin=ft.margin.only(bottom=16),
                    ),
                    
                    ft.Text("New Password", size=12, color=c["text_secondary"]),
                    ft.TextField(
                        ref=new_password_field,
                        hint_text="Create a strong password",
                        prefix_icon=ft.Icons.LOCK_OUTLINED,
                        password=True, can_reveal_password=True,
                        border_color=c["border"], focused_border_color="#4CAF50",
                        hint_style=ft.TextStyle(color=c["text_hint"]),
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        cursor_color="#4CAF50", border_radius=10,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=12, color=c["text_secondary"]),
                                ft.Text("At least 8 characters", size=10, color=c["text_secondary"]),
                            ], spacing=4),
                            ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=12, color=c["text_secondary"]),
                                ft.Text("At least one number", size=10, color=c["text_secondary"]),
                            ], spacing=4),
                        ], spacing=2),
                        margin=ft.margin.only(left=8, bottom=12),
                    ),
                    
                    ft.Text("Confirm Password", size=12, color=c["text_secondary"]),
                    ft.TextField(
                        ref=confirm_password_field,
                        hint_text="Re-enter your password",
                        prefix_icon=ft.Icons.LOCK_OUTLINED,
                        password=True, can_reveal_password=True,
                        border_color=c["border"], focused_border_color="#4CAF50",
                        hint_style=ft.TextStyle(color=c["text_hint"]),
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        cursor_color="#4CAF50", border_radius=10,
                        on_submit=handle_action,
                    ),
                ], spacing=6),
                visible=False,
            ),
            
            ft.Container(height=8),
            
            # Info note
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color="#FFC107"),
                    ft.Column([
                        ft.Text("Reset via Email", size=11, weight=ft.FontWeight.W_600, color="#FFC107"),
                        ft.Text(
                            "A 6-digit code will be sent to your CSPC email. "
                            "In demo mode, the code may also appear in a notification.",
                            size=10,
                            color=c["text_secondary"],
                        ),
                    ], spacing=0, expand=True),
                ], spacing=10),
                bgcolor=c["accent_bg"], padding=12, border_radius=8,
            ),
            
            ft.Container(height=16),
            
            # Action buttons
            ft.Row([
                ft.ElevatedButton(
                    content=ft.Text("Cancel", size=14),
                    bgcolor=c["border"], color=c["text_primary"],
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    on_click=handle_back,
                    expand=True,
                ),
                ft.Container(width=12),
                ft.ElevatedButton(
                    ref=action_btn,
                    content=ft.Row([
                        ft.Icon(ft.Icons.SEND, size=18),
                        ft.Text("Send Code", size=14, weight=ft.FontWeight.W_600),
                    ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor="#4CAF50", color="#ffffff",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    on_click=handle_action,
                    expand=True,
                ),
            ]),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        bgcolor=c["bg_card"], padding=24, border_radius=16,
        width=400,
        border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
    )
    
    return ft.Container(
        content=ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=c["text_primary"],
                        on_click=handle_back,
                    ),
                    ft.Column([
                        ft.Text("Reset Password", size=20, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                        ft.Text("Recover your CSPC account", size=12, color=c["text_secondary"]),
                    ], spacing=0),
                ], spacing=8),
                margin=ft.margin.only(bottom=20),
            ),
            
            # Centered card
            ft.Container(
                content=ft.ResponsiveRow([
                    ft.Column(
                        controls=[content_card],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        col={"xs": 12, "sm": 10, "md": 8, "lg": 6},
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
            ),
            
            # Back to login
            ft.Container(
                content=ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ARROW_BACK, size=16, color="#4CAF50"),
                        ft.Text("Back to Sign In", size=13, color="#4CAF50"),
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                    on_click=lambda e: on_back() if on_back else None,
                ),
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=16),
            ),
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=c["bg_primary"],
        expand=True,
        padding=ft.padding.symmetric(vertical=16, horizontal=20),
    )
