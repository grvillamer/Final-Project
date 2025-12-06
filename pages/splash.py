"""
Smart Classroom Availability and Locator App for CCS - Splash Screen
"""
import flet as ft
import asyncio


def SplashPage(page: ft.Page, on_complete=None):
    """Splash screen with animated logo"""
    
    # Animation state
    logo_scale = ft.Ref[ft.Container]()
    
    async def animate_and_navigate():
        await asyncio.sleep(2.5)
        if on_complete:
            on_complete()
    
    # Start animation
    page.run_task(animate_and_navigate)
    
    return ft.Container(
        content=ft.Column(
            controls=[
                # Logo and branding
                ft.Container(
                    content=ft.Column(
                        controls=[
                            # CCS Logo
                            ft.Container(
                                content=ft.Text(
                                    "🏫",
                                    size=56,
                                ),
                                animate_scale=1000,
                                animate_opacity=1000,
                            ),
                            ft.Text(
                                "Smart Classroom",
                                size=32,
                                weight=ft.FontWeight.W_800,
                                color="#4CAF50",
                            ),
                            ft.Text(
                                "Availability & Locator",
                                size=24,
                                weight=ft.FontWeight.W_600,
                                color="#4CAF50",
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "for CCS",
                                    size=18,
                                    weight=ft.FontWeight.W_500,
                                    color="#8b95a5",
                                ),
                                margin=ft.margin.only(top=4),
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "Camarines Sur Polytechnic Colleges",
                                    size=12,
                                    color="#5a6474",
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                margin=ft.margin.only(top=8),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    ref=logo_scale,
                ),
                
                # Loading indicator
                ft.Container(
                    content=ft.ProgressRing(
                        width=36,
                        height=36,
                        stroke_width=3,
                        color="#4CAF50",
                    ),
                    margin=ft.margin.only(top=60),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        ),
        bgcolor="#0d1520",
        expand=True,
        alignment=ft.alignment.center,
    )
