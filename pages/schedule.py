"""
Smart Classroom - Class Schedule Page
Semester Class Timetable showing day, time, and room assignments
"""
import flet as ft
from database import db
from datetime import datetime, timedelta
from utils.helpers import get_initials
from utils.theme import get_theme


def SchedulePage(page: ft.Page, user: dict, on_navigate=None):
    """Schedule page showing semester class timetable"""
    
    def t():
        return get_theme(page)
    
    c = t()
    
    user_id = user.get('id')
    user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
    is_instructor = user.get('role') == 'instructor'
    
    # State
    view_mode = {"value": "timetable"}  # timetable or list
    current_semester = {"value": "1st Semester 2024-2025"}
    
    # Refs
    content_container = ft.Ref[ft.Container]()
    
    def get_all_class_schedules():
        """Get all class schedules grouped by day"""
        classrooms = db.get_all_classrooms()
        all_schedules = []
        
        # Get schedules for the next 7 days to capture all weekly patterns
        today = datetime.now()
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            day_name = date.strftime("%A")
            
            for room in classrooms:
                schedules = db.get_room_schedules(room['id'], date_str)
                for sched in schedules:
                    sched['room_name'] = room['name']
                    sched['room_code'] = room['code']
                    sched['room_floor'] = room['floor']
                    sched['day'] = day_name
                    
                    # Parse day from notes if available
                    notes = sched.get('notes', '')
                    if 'Day:' in notes:
                        try:
                            day_part = notes.split('Day:')[1].split('|')[0].strip()
                            sched['day'] = day_part
                        except:
                            pass
                    
                    all_schedules.append(sched)
        
        return all_schedules
    
    def get_instructor_schedules():
        """Get schedules for the current instructor"""
        if not is_instructor:
            return []
        return db.get_instructor_schedules(user_id)
    
    def update_content():
        c = t()
        if view_mode["value"] == "timetable":
            content_container.current.content = build_timetable_view()
        else:
            content_container.current.content = build_list_view()
        page.update()
    
    def toggle_view(mode: str):
        view_mode["value"] = mode
        update_content()
    
    def show_delete_schedule_dialog(schedule):
        """Show confirmation dialog to delete a schedule"""
        c = t()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def confirm_delete(e):
            success = db.delete_room_schedule(schedule.get('id'))
            dialog.open = False
            
            if success:
                page.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="#ffffff", size=18),
                        ft.Text("Schedule deleted successfully", color="#ffffff"),
                    ], spacing=8),
                    bgcolor=c["success"],
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ERROR, color="#ffffff", size=18),
                        ft.Text("Failed to delete schedule", color="#ffffff"),
                    ], spacing=8),
                    bgcolor=c["error"],
                )
            
            page.snack_bar.open = True
            update_content()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.DELETE_OUTLINE, color=c["error"], size=24),
                ft.Text("Delete Schedule", size=16, weight=ft.FontWeight.W_600, color=c["text_primary"]),
            ], spacing=8),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Are you sure you want to delete this class schedule?", 
                           size=13, color=c["text_secondary"]),
                    ft.Container(height=12),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(schedule.get('subject_name', 'Class'), size=14, 
                                   weight=ft.FontWeight.W_600, color=c["text_primary"]),
                            ft.Text(f"{schedule.get('start_time', '')} - {schedule.get('end_time', '')}", 
                                   size=12, color=c["text_secondary"]),
                            ft.Text(f"{schedule.get('room_name', 'Room')}", size=11, color=c["text_hint"]),
                        ], spacing=4),
                        bgcolor=c["bg_secondary"], padding=12, border_radius=8,
                    ),
                    ft.Container(height=8),
                    ft.Text("This action cannot be undone.", size=11, color=c["text_hint"]),
                ], spacing=4),
                width=280,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog, style=ft.ButtonStyle(color=c["text_secondary"])),
                ft.ElevatedButton("Delete", bgcolor=c["error"], color="#ffffff",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def build_class_block(schedule, compact=False):
        """Build a class block for the timetable"""
        c = t()
        
        # Parse section from notes
        notes = schedule.get('notes', '')
        section = ""
        if 'Section:' in notes:
            try:
                section = notes.split('Section:')[1].strip()
            except:
                pass
        
        # Check if this is the instructor's own schedule
        is_own_schedule = is_instructor and schedule.get('instructor_id') == user_id
        
        if compact:
            return ft.Container(
                content=ft.Column([
                    ft.Text(schedule['subject_name'][:15] + "..." if len(schedule['subject_name']) > 15 else schedule['subject_name'], 
                           size=9, color="#ffffff", weight=ft.FontWeight.W_600, max_lines=1),
                    ft.Text(f"{schedule['start_time'][:5]}-{schedule['end_time'][:5]}", size=8, color="#ffffffcc"),
                    ft.Text(schedule.get('room_code', ''), size=7, color="#ffffffaa"),
                ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=c["accent"], padding=6, border_radius=6, width=70,
                alignment=ft.alignment.center,
            )
        
        # Build content with optional delete button for instructors
        content_rows = [
            ft.Row([
                ft.Container(width=4, height=40, bgcolor=c["accent"], border_radius=2),
                ft.Column([
                    ft.Text(schedule['subject_name'], size=13, weight=ft.FontWeight.W_600, 
                           color=c["text_primary"], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{schedule['start_time']} - {schedule['end_time']}", size=11, color=c["accent"]),
                ], spacing=2, expand=True),
                # Delete button for instructor's own schedules
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=c["error"],
                    icon_size=18,
                    tooltip="Delete this schedule",
                    on_click=lambda e, s=schedule: show_delete_schedule_dialog(s),
                ) if is_own_schedule else ft.Container(),
            ], spacing=10),
            ft.Row([
                ft.Icon(ft.Icons.MEETING_ROOM, size=12, color=c["text_secondary"]),
                ft.Text(schedule.get('room_name', 'Room'), size=11, color=c["text_secondary"]),
                ft.Text(f"• {schedule.get('room_floor', '')} Floor", size=10, color=c["text_hint"]),
            ], spacing=4),
        ]
        
        if schedule.get('instructor_name'):
            content_rows.append(
                ft.Row([
                    ft.Icon(ft.Icons.PERSON_OUTLINE, size=12, color=c["text_hint"]),
                    ft.Text(schedule.get('instructor_name', 'Instructor'), size=10, color=c["text_hint"]),
                    ft.Text(f"• {section}" if section else "", size=10, color=c["text_hint"]),
                ], spacing=4)
            )
        
        return ft.Container(
            content=ft.Column(content_rows, spacing=6),
            bgcolor=c["bg_card"], padding=12, border_radius=10,
            border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
        )
    
    def time_to_minutes(time_str: str) -> int:
        """Convert time string (HH:MM) to minutes from midnight"""
        try:
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        except:
            return 0
    
    def build_timetable_view():
        """Build weekly timetable grid view with time-spanning blocks"""
        c = t()
        schedules = get_all_class_schedules()
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
        # Time range: 7:00 AM to 9:00 PM (in 30-min increments for better precision)
        start_hour = 7
        end_hour = 21
        slot_height = 30  # Height per 30-min slot
        
        # Group schedules by day
        schedules_by_day = {day: [] for day in days}
        for sched in schedules:
            day = sched.get('day', '')
            if day in schedules_by_day:
                schedules_by_day[day].append(sched)
        
        # Build time column
        time_labels = []
        for hour in range(start_hour, end_hour + 1):
            if hour == 12:
                display_time = "12:00 PM"
            elif hour > 12:
                display_time = f"{hour-12}:00 PM"
            else:
                display_time = f"{hour}:00 AM"
            
            time_labels.append(
                ft.Container(
                    content=ft.Text(display_time, size=9, color=c["text_secondary"]),
                    height=slot_height * 2,  # Each hour = 2 slots (30 min each)
                    alignment=ft.alignment.top_right,
                    padding=ft.padding.only(right=6, top=0),
                )
            )
        
        time_column = ft.Container(
            content=ft.Column(time_labels, spacing=0),
            width=55,
        )
        
        # Build day columns with class blocks
        day_columns = []
        for day in days:
            day_schedules = schedules_by_day[day]
            
            # Create a stack for this day to allow overlapping positioning
            day_blocks = []
            
            # Background grid lines (hourly)
            for i in range(end_hour - start_hour + 1):
                day_blocks.append(
                    ft.Container(
                        bgcolor=c["bg_secondary"] if i % 2 == 0 else c["bg_primary"],
                        border=ft.border.only(bottom=ft.BorderSide(1, c["border"])),
                        width=70,
                        height=slot_height * 2,
                        top=i * slot_height * 2,
                        left=0,
                    )
                )
            
            # Add class blocks
            for sched in day_schedules:
                start_mins = time_to_minutes(sched['start_time'])
                end_mins = time_to_minutes(sched['end_time'])
                
                # Calculate position and height
                grid_start_mins = start_hour * 60
                top_offset = ((start_mins - grid_start_mins) / 30) * slot_height
                duration_mins = end_mins - start_mins
                block_height = (duration_mins / 30) * slot_height
                
                if top_offset < 0 or block_height <= 0:
                    continue
                
                # Check if this is the instructor's own schedule
                is_own_schedule = is_instructor and sched.get('instructor_id') == user_id
                
                # Parse section from notes
                notes = sched.get('notes', '')
                section = ""
                if 'Section:' in notes:
                    try:
                        section = notes.split('Section:')[1].strip()
                    except:
                        pass
                
                # Format times for display
                start_time_display = sched['start_time'][:5]
                end_time_display = sched['end_time'][:5]
                
                # Create class block with time indicators
                class_content = ft.Column([
                    # Start time indicator at top
                    ft.Container(
                        content=ft.Text(start_time_display, size=8, color="#ffffffcc", 
                                       weight=ft.FontWeight.W_600),
                        bgcolor="#00000033",
                        padding=ft.padding.symmetric(horizontal=4, vertical=1),
                        border_radius=3,
                    ),
                    ft.Container(expand=True),
                    # Subject name in center
                    ft.Text(
                        sched['subject_name'][:12] + "..." if len(sched['subject_name']) > 12 else sched['subject_name'],
                        size=9, color="#ffffff", weight=ft.FontWeight.W_700,
                        text_align=ft.TextAlign.CENTER, max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(sched.get('room_code', ''), size=7, color="#ffffffbb"),
                    ft.Container(expand=True),
                    # End time indicator at bottom
                    ft.Container(
                        content=ft.Text(end_time_display, size=8, color="#ffffffcc",
                                       weight=ft.FontWeight.W_600),
                        bgcolor="#00000033",
                        padding=ft.padding.symmetric(horizontal=4, vertical=1),
                        border_radius=3,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)
                
                # Shorter blocks get simplified content
                if block_height < 60:
                    class_content = ft.Column([
                        ft.Text(f"{start_time_display}", size=7, color="#ffffffcc"),
                        ft.Text(
                            sched['subject_name'][:8] + "..." if len(sched['subject_name']) > 8 else sched['subject_name'],
                            size=8, color="#ffffff", weight=ft.FontWeight.W_600, max_lines=1,
                        ),
                        ft.Text(f"{end_time_display}", size=7, color="#ffffffcc"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1)
                
                day_blocks.append(
                    ft.Container(
                        content=class_content,
                        bgcolor=c["accent"],
                        border_radius=6,
                        width=66,
                        height=max(block_height - 2, 30),
                        top=top_offset + 1,
                        left=2,
                        padding=ft.padding.symmetric(horizontal=4, vertical=4),
                        shadow=ft.BoxShadow(
                            spread_radius=0, blur_radius=4,
                            color="#00000022", offset=ft.Offset(0, 2),
                        ),
                        tooltip=f"{sched['subject_name']}\n{sched['start_time']} - {sched['end_time']}\n{sched.get('room_name', '')}\n{sched.get('instructor_name', '')}",
                    )
                )
            
            # Calculate total height
            total_height = (end_hour - start_hour + 1) * slot_height * 2
            
            day_columns.append(
                ft.Column([
                    # Day header
                    ft.Container(
                        content=ft.Text(day[:3], size=11, weight=ft.FontWeight.W_600,
                                       color=c["text_primary"], text_align=ft.TextAlign.CENTER),
                        width=70, height=28, alignment=ft.alignment.center,
                        bgcolor=c["bg_card"],
                        border_radius=ft.border_radius.only(top_left=8, top_right=8),
                    ),
                    # Day schedule stack
                    ft.Container(
                        content=ft.Stack(day_blocks),
                        width=70,
                        height=total_height,
                    ),
                ], spacing=0)
            )
        
        # Legend
        legend = ft.Container(
            content=ft.Row([
                ft.Container(width=12, height=12, bgcolor=c["accent"], border_radius=3),
                ft.Text("Scheduled Class", size=10, color=c["text_secondary"]),
                ft.Container(width=12),
                ft.Icon(ft.Icons.ACCESS_TIME, size=12, color=c["text_hint"]),
                ft.Text("Time shown at start & end", size=10, color=c["text_hint"]),
            ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=10),
        )
        
        # Main timetable
        timetable = ft.Row([
            ft.Column([
                ft.Container(height=28),  # Spacer for header alignment
                time_column,
            ], spacing=0),
            *day_columns,
        ], spacing=2, scroll=ft.ScrollMode.AUTO)
        
        return ft.Column([
            legend,
            ft.Container(
                content=timetable,
                expand=True,
            ),
        ], expand=True, scroll=ft.ScrollMode.AUTO)
    
    def build_list_view():
        """Build list view of schedules by day"""
        c = t()
        schedules = get_all_class_schedules() if not is_instructor else get_instructor_schedules()
        
        if not schedules:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.EVENT_BUSY, size=48, color=c["text_hint"]),
                    ft.Text("No classes scheduled", size=16, weight=ft.FontWeight.W_500, color=c["text_primary"]),
                    ft.Text("Set up your class schedule from the Home page", size=12, color=c["text_secondary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.alignment.center, padding=40,
            )
        
        # Group by day
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        schedules_by_day = {day: [] for day in days_order}
        
        for sched in schedules:
            day = sched.get('day', '')
            # Try to parse from notes
            notes = sched.get('notes', '')
            if 'Day:' in notes:
                try:
                    day = notes.split('Day:')[1].split('|')[0].strip()
                except:
                    pass
            
            if day in schedules_by_day:
                schedules_by_day[day].append(sched)
        
        # Sort each day by start time
        for day in schedules_by_day:
            schedules_by_day[day].sort(key=lambda x: x.get('start_time', ''))
        
        sections = []
        for day in days_order:
            day_scheds = schedules_by_day[day]
            if day_scheds:
                sections.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=c["accent"]),
                            ft.Text(day, size=14, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                            ft.Text(f"({len(day_scheds)} classes)", size=11, color=c["text_secondary"]),
                        ], spacing=8),
                        padding=ft.padding.only(top=16, bottom=8),
                    )
                )
                for sched in day_scheds:
                    sections.append(build_class_block(sched))
        
        if not sections:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=48, color=c["text_hint"]),
                    ft.Text("No scheduled classes", size=16, color=c["text_primary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.alignment.center, padding=40,
            )
        
        return ft.Column(sections, spacing=8, scroll=ft.ScrollMode.AUTO)
    
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
                            ft.Text("Class Schedule", size=16, weight=ft.FontWeight.W_700, color=c["text_primary"]),
                            ft.Text(current_semester["value"], size=11, color=c["text_secondary"]),
                        ], spacing=0),
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ),
            
            ft.Container(height=16),
            
            # Semester selector
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SCHOOL, size=16, color=c["accent"]),
                    ft.Dropdown(
                        value=current_semester["value"],
                        options=[
                            ft.dropdown.Option("1st Semester 2024-2025"),
                            ft.dropdown.Option("2nd Semester 2024-2025"),
                            ft.dropdown.Option("Summer 2025"),
                        ],
                        border_color="transparent",
                        text_style=ft.TextStyle(color=c["text_primary"], size=12, weight=ft.FontWeight.W_500),
                        content_padding=ft.padding.symmetric(horizontal=8),
                        on_change=lambda e: None,  # Could filter by semester
                    ),
                ], spacing=8),
                bgcolor=c["bg_card"], padding=ft.padding.symmetric(horizontal=12, vertical=4),
                border_radius=8,
                border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            ),
            
            ft.Container(height=12),
            
            # View toggle
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.GRID_VIEW, size=16, 
                                   color=c["accent"] if view_mode["value"] == "timetable" else c["text_secondary"]),
                            ft.Text("Timetable", size=12, 
                                   color=c["accent"] if view_mode["value"] == "timetable" else c["text_secondary"]),
                        ], spacing=4),
                        bgcolor=c["accent_bg"] if view_mode["value"] == "timetable" else "transparent",
                        padding=ft.padding.symmetric(horizontal=14, vertical=8), border_radius=16,
                        on_click=lambda e: toggle_view("timetable"),
                        ink=True,
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LIST, size=16,
                                   color=c["accent"] if view_mode["value"] == "list" else c["text_secondary"]),
                            ft.Text("List", size=12,
                                   color=c["accent"] if view_mode["value"] == "list" else c["text_secondary"]),
                        ], spacing=4),
                        bgcolor=c["accent_bg"] if view_mode["value"] == "list" else "transparent",
                        padding=ft.padding.symmetric(horizontal=14, vertical=8), border_radius=16,
                        on_click=lambda e: toggle_view("list"),
                        ink=True,
                    ),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=c["bg_card"], padding=6, border_radius=20,
                border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            ),
            
            ft.Container(height=16),
            
            # Info card for instructors
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=c["info"]),
                    ft.Text(
                        "To set up a class, go to Home → Select an available room → Set Class",
                        size=11, color=c["text_secondary"], expand=True,
                    ),
                ], spacing=8),
                bgcolor=c["bg_card"], padding=12, border_radius=8,
                border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
                visible=is_instructor,
            ),
            
            ft.Container(height=8) if is_instructor else ft.Container(),
            
            # Schedule content
            ft.Container(
                ref=content_container,
                content=build_list_view(),  # Start with list view for better mobile experience
                expand=True,
            ),
        ], scroll=ft.ScrollMode.AUTO, spacing=0),
        bgcolor=c["bg_primary"],
        expand=True,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
