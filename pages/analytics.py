"""
SpottEd Analytics Page - AI-Powered Attendance Insights
"""
import flet as ft
from database import db
from components.cards import AnalyticsCard, StatsCard
from utils.helpers import (
    calculate_attendance_rate, 
    get_attendance_status_color,
    predict_attendance,
    identify_at_risk_students,
    generate_recommendations,
    get_day_of_week_stats
)


def AnalyticsPage(page: ft.Page, user: dict, on_navigate=None):
    """AI-powered analytics dashboard"""
    
    is_instructor = user.get('role') == 'instructor'
    
    if is_instructor:
        return InstructorAnalyticsPage(page, user, on_navigate)
    else:
        return StudentAnalyticsPage(page, user, on_navigate)


def InstructorAnalyticsPage(page: ft.Page, user: dict, on_navigate=None):
    """Instructor analytics dashboard with AI insights"""
    
    classes = db.get_classes_by_instructor(user['id'])
    selected_class = ft.Ref[ft.Dropdown]()
    analytics_content = ft.Ref[ft.Column]()
    
    def load_analytics(class_id):
        analytics = db.get_class_analytics(class_id)
        
        # AI predictions
        prediction = predict_attendance(analytics.get('sessions_data', []))
        at_risk = identify_at_risk_students(analytics.get('students_data', []))
        recommendations = generate_recommendations({
            'overall_attendance_rate': analytics.get('overall_attendance_rate', 0),
            'trend': prediction.get('trend', 'stable'),
            'students_data': analytics.get('students_data', [])
        })
        
        return analytics, prediction, at_risk, recommendations
    
    def build_analytics_ui(class_id):
        analytics, prediction, at_risk, recommendations = load_analytics(class_id)
        
        rate = analytics.get('overall_attendance_rate', 0)
        
        controls = [
            # Overview stats
            ft.Row(
                controls=[
                    StatsCard(
                        title="Attendance Rate",
                        value=f"{rate}%",
                        icon=ft.Icons.PIE_CHART_OUTLINED,
                        color=get_attendance_status_color(rate),
                    ),
                    StatsCard(
                        title="Total Sessions",
                        value=str(analytics.get('total_sessions', 0)),
                        icon=ft.Icons.CALENDAR_TODAY,
                        color="#2196F3",
                    ),
                ],
                spacing=12,
            ),
            
            # AI Prediction Card
            AnalyticsCard(
                title="🤖 AI Prediction",
                icon=ft.Icons.AUTO_AWESOME,
                children=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Predicted Rate",
                                        size=12,
                                        color="#8b95a5",
                                    ),
                                    ft.Text(
                                        f"{prediction.get('predicted_rate', 0)}%",
                                        size=28,
                                        weight=ft.FontWeight.W_700,
                                        color=get_attendance_status_color(prediction.get('predicted_rate', 0)),
                                    ),
                                ],
                                expand=True,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Confidence",
                                        size=12,
                                        color="#8b95a5",
                                    ),
                                    ft.Text(
                                        f"{prediction.get('confidence', 0)}%",
                                        size=20,
                                        weight=ft.FontWeight.W_600,
                                        color="#8b95a5",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.TRENDING_UP if prediction.get('trend') == 'improving' else (
                                                ft.Icons.TRENDING_DOWN if prediction.get('trend') == 'declining' else ft.Icons.TRENDING_FLAT
                                            ),
                                            size=16,
                                            color="#4CAF50" if prediction.get('trend') == 'improving' else (
                                                "#F44336" if prediction.get('trend') == 'declining' else "#8b95a5"
                                            ),
                                        ),
                                        ft.Text(
                                            prediction.get('trend', 'stable').capitalize(),
                                            size=12,
                                            color="#4CAF50" if prediction.get('trend') == 'improving' else (
                                                "#F44336" if prediction.get('trend') == 'declining' else "#8b95a5"
                                            ),
                                        ),
                                    ],
                                    spacing=4,
                                ),
                                bgcolor="#0d1520",
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                border_radius=12,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    f"Risk: {prediction.get('risk_level', 'unknown').upper()}",
                                    size=11,
                                    weight=ft.FontWeight.W_600,
                                    color="#ffffff",
                                ),
                                bgcolor="#F44336" if prediction.get('risk_level') == 'high' else (
                                    "#FF9800" if prediction.get('risk_level') == 'medium' else "#4CAF50"
                                ),
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                border_radius=12,
                            ),
                        ],
                        spacing=8,
                    ),
                ],
            ),
            
            # AI Recommendations
            AnalyticsCard(
                title="💡 AI Recommendations",
                icon=ft.Icons.LIGHTBULB_OUTLINED,
                children=[
                    ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    rec,
                                    size=13,
                                    color="#ffffff",
                                ),
                                padding=ft.padding.symmetric(vertical=6),
                            )
                            for rec in recommendations
                        ],
                        spacing=4,
                    ),
                ],
            ),
            
            # At-Risk Students
            AnalyticsCard(
                title="⚠️ At-Risk Students",
                icon=ft.Icons.WARNING_OUTLINED,
                children=[
                    ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=ft.Text(
                                                f"{s.get('first_name', '')[0]}{s.get('last_name', '')[0]}",
                                                size=12,
                                                weight=ft.FontWeight.W_600,
                                                color="#ffffff",
                                            ),
                                            width=36,
                                            height=36,
                                            bgcolor="#F44336" if s.get('risk_level') == 'high' else "#FF9800",
                                            border_radius=18,
                                            alignment=ft.alignment.center,
                                        ),
                                        ft.Column(
                                            controls=[
                                                ft.Text(
                                                    f"{s.get('first_name', '')} {s.get('last_name', '')}",
                                                    size=14,
                                                    weight=ft.FontWeight.W_500,
                                                    color="#ffffff",
                                                ),
                                                ft.Text(
                                                    f"{s.get('attendance_rate', 0)}% attendance • {s.get('missed_sessions', 0)} missed",
                                                    size=11,
                                                    color="#8b95a5",
                                                ),
                                            ],
                                            spacing=2,
                                            expand=True,
                                        ),
                                    ],
                                    spacing=12,
                                ),
                                padding=ft.padding.symmetric(vertical=6),
                            )
                            for s in at_risk[:5]
                        ] if at_risk else [
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="#4CAF50", size=20),
                                        ft.Text(
                                            "No at-risk students! 🎉",
                                            size=14,
                                            color="#4CAF50",
                                        ),
                                    ],
                                    spacing=8,
                                ),
                                padding=8,
                            ),
                        ],
                        spacing=4,
                    ),
                ],
            ),
            
            # Attendance by Student
            AnalyticsCard(
                title="📊 Student Rankings",
                icon=ft.Icons.LEADERBOARD,
                children=[
                    ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Text(
                                            f"#{i+1}",
                                            size=12,
                                            weight=ft.FontWeight.W_700,
                                            color="#4CAF50" if i < 3 else "#8b95a5",
                                            width=30,
                                        ),
                                        ft.Text(
                                            f"{s.get('first_name', '')} {s.get('last_name', '')}",
                                            size=13,
                                            color="#ffffff",
                                            expand=True,
                                        ),
                                        ft.Text(
                                            f"{calculate_attendance_rate(s.get('present_count', 0), s.get('late_count', 0), s.get('total_sessions', 1))}%",
                                            size=13,
                                            weight=ft.FontWeight.W_600,
                                            color=get_attendance_status_color(
                                                calculate_attendance_rate(
                                                    s.get('present_count', 0), 
                                                    s.get('late_count', 0), 
                                                    s.get('total_sessions', 1)
                                                )
                                            ),
                                        ),
                                    ],
                                ),
                                padding=ft.padding.symmetric(vertical=6),
                            )
                            for i, s in enumerate(sorted(
                                analytics.get('students_data', []),
                                key=lambda x: calculate_attendance_rate(
                                    x.get('present_count', 0),
                                    x.get('late_count', 0),
                                    x.get('total_sessions', 1)
                                ),
                                reverse=True
                            )[:10])
                        ],
                        spacing=0,
                    ),
                ],
            ),
        ]
        
        return controls
    
    def handle_class_change(e):
        if selected_class.current.value:
            class_id = int(selected_class.current.value)
            analytics_content.current.controls = build_analytics_ui(class_id)
            page.update()
    
    initial_controls = []
    if classes:
        initial_controls = build_analytics_ui(classes[0]['id'])
    
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Text(
                    "Analytics",
                    size=24,
                    weight=ft.FontWeight.W_700,
                    color="#ffffff",
                ),
                ft.Text(
                    "AI-powered attendance insights",
                    size=14,
                    color="#8b95a5",
                ),
                
                ft.Container(height=16),
                
                # Class selector
                ft.Dropdown(
                    ref=selected_class,
                    label="Select Class",
                    value=str(classes[0]['id']) if classes else None,
                    options=[
                        ft.dropdown.Option(str(c['id']), c['name'])
                        for c in classes
                    ],
                    border_color="#2d3a4d",
                    focused_border_color="#4CAF50",
                    label_style=ft.TextStyle(color="#8b95a5"),
                    text_style=ft.TextStyle(color="#ffffff"),
                    border_radius=10,
                    on_change=handle_class_change,
                ) if classes else ft.Container(),
                
                ft.Container(height=20),
                
                # Analytics content
                ft.Column(
                    ref=analytics_content,
                    controls=initial_controls if classes else [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.ANALYTICS_OUTLINED, size=64, color="#8b95a5"),
                                    ft.Text("No classes yet", size=16, color="#8b95a5"),
                                    ft.Text("Create a class to see analytics", size=13, color="#5a6474"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            padding=60,
                            alignment=ft.alignment.center,
                        ),
                    ],
                    spacing=16,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor="#0d1520",
        expand=True,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
    )


def StudentAnalyticsPage(page: ft.Page, user: dict, on_navigate=None):
    """Student analytics dashboard"""
    
    analytics = db.get_student_analytics(user['id'])
    
    rate = analytics.get('overall_attendance_rate', 0)
    present = analytics.get('present_count', 0)
    late = analytics.get('late_count', 0)
    total = analytics.get('total_sessions', 0)
    
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Text(
                    "My Analytics",
                    size=24,
                    weight=ft.FontWeight.W_700,
                    color="#ffffff",
                ),
                ft.Text(
                    "Your attendance performance",
                    size=14,
                    color="#8b95a5",
                ),
                
                ft.Container(height=20),
                
                # Overview stats
                ft.Row(
                    controls=[
                        StatsCard(
                            title="Attendance Rate",
                            value=f"{rate}%",
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINED,
                            color=get_attendance_status_color(rate),
                        ),
                        StatsCard(
                            title="Classes",
                            value=str(analytics.get('total_classes', 0)),
                            icon=ft.Icons.SCHOOL_OUTLINED,
                            color="#2196F3",
                        ),
                    ],
                    spacing=12,
                ),
                
                ft.Container(height=16),
                
                # Attendance breakdown
                AnalyticsCard(
                    title="Attendance Breakdown",
                    icon=ft.Icons.PIE_CHART_OUTLINED,
                    children=[
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(str(present), size=32, weight=ft.FontWeight.W_700, color="#4CAF50"),
                                        ft.Text("Present", size=12, color="#8b95a5"),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    expand=True,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(str(late), size=32, weight=ft.FontWeight.W_700, color="#FFC107"),
                                        ft.Text("Late", size=12, color="#8b95a5"),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    expand=True,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(str(total - present - late), size=32, weight=ft.FontWeight.W_700, color="#F44336"),
                                        ft.Text("Absent", size=12, color="#8b95a5"),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    expand=True,
                                ),
                            ],
                        ),
                        ft.ProgressBar(
                            value=rate / 100 if total > 0 else 0,
                            color=get_attendance_status_color(rate),
                            bgcolor="#2d3a4d",
                            height=8,
                            border_radius=4,
                        ),
                    ],
                ),
                
                # By class breakdown
                AnalyticsCard(
                    title="By Class",
                    icon=ft.Icons.SCHOOL_OUTLINED,
                    children=[
                        ft.Column(
                            controls=[
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(
                                                        c.get('name', 'Unknown'),
                                                        size=14,
                                                        weight=ft.FontWeight.W_500,
                                                        color="#ffffff",
                                                    ),
                                                    ft.Text(
                                                        f"{c.get('present', 0)}/{c.get('total_sessions', 0)} sessions",
                                                        size=11,
                                                        color="#8b95a5",
                                                    ),
                                                ],
                                                spacing=2,
                                                expand=True,
                                            ),
                                            ft.Text(
                                                f"{calculate_attendance_rate(c.get('present', 0), c.get('late', 0), c.get('total_sessions', 1))}%",
                                                size=16,
                                                weight=ft.FontWeight.W_700,
                                                color=get_attendance_status_color(
                                                    calculate_attendance_rate(
                                                        c.get('present', 0),
                                                        c.get('late', 0),
                                                        c.get('total_sessions', 1)
                                                    )
                                                ),
                                            ),
                                        ],
                                    ),
                                    padding=ft.padding.symmetric(vertical=8),
                                )
                                for c in analytics.get('classes_data', [])
                            ] if analytics.get('classes_data') else [
                                ft.Text("No class data yet", size=14, color="#8b95a5"),
                            ],
                            spacing=0,
                        ),
                    ],
                ),
                
                # Performance tip
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.TIPS_AND_UPDATES, color="#FFC107", size=24),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Performance Tip",
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color="#ffffff",
                                    ),
                                    ft.Text(
                                        "Great job!" if rate >= 90 else (
                                            "Keep it up! Aim for 90%+ attendance." if rate >= 75 else
                                            "Your attendance needs improvement. Try to attend more classes."
                                        ),
                                        size=12,
                                        color="#8b95a5",
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=12,
                    ),
                    bgcolor="#1a2332",
                    padding=16,
                    border_radius=12,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor="#0d1520",
        expand=True,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
    )



