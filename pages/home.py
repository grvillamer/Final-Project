"""
SpottEd Home Page - CSPC Smart Classroom Availability and Locator App
Full Classroom Management Interface with Search, Filters, Map View, and Scheduling
"""
import flet as ft
from database import db
from datetime import datetime, timedelta
from utils.helpers import get_initials
from utils.theme import get_theme


def HomePage(page: ft.Page, user: dict, on_navigate=None):
    """Home dashboard with classroom management, search, filters, and map view"""
    
    # Theme colors
    def t():
        return get_theme(page)
    
    c = t()
    
    user_name = user.get('first_name', 'User')
    initials = get_initials(user.get('first_name', ''), user.get('last_name', ''))
    student_id = user.get('student_id', '')
    is_instructor = user.get('role') == 'instructor'
    is_admin = user.get('role') == 'admin'
    user_id = user.get('id')
    
    # State
    current_view = {"value": "list"}  # list, map, schedule
    current_filters = {"type": "all", "floor": "all", "status": "all"}
    search_query = {"value": ""}
    schedule_view = {"value": "daily"}  # daily, weekly
    selected_date = {"value": datetime.now().strftime("%Y-%m-%d")}
    
    # Refs
    search_field = ft.Ref[ft.TextField]()
    content_container = ft.Ref[ft.Container]()
    type_dropdown = ft.Ref[ft.Dropdown]()
    floor_dropdown = ft.Ref[ft.Dropdown]()
    status_dropdown = ft.Ref[ft.Dropdown]()
    no_results_container = ft.Ref[ft.Container]()
    
    def load_classrooms():
        """Load classrooms from database with current schedules"""
        rooms = db.get_all_classrooms()
        today = datetime.now().strftime("%Y-%m-%d")
        
        classroom_list = []
        for room in rooms:
            schedules = db.get_room_schedules(room['id'], today)
            current_time = datetime.now().strftime("%H:%M")
            
            current_class = None
            for sched in schedules:
                if sched['start_time'] <= current_time <= sched['end_time']:
                    current_class = {
                        "name": sched['subject_name'],
                        "time": f"{sched['start_time']} - {sched['end_time']}",
                        "instructor": sched['instructor_name'],
                        "schedule_id": sched['id']
                    }
                    break
            
            status = "occupied" if current_class else "available"
            if room['status'] == 'maintenance':
                status = "maintenance"
            
            # Determine room type from name
            room_type = "lecture"
            name_lower = room['name'].lower()
            if "lab" in name_lower or "computer" in name_lower:
                room_type = "laboratory"
            elif "library" in name_lower:
                room_type = "library"
            elif "conference" in name_lower or "meeting" in name_lower:
                room_type = "conference"
            
            classroom_list.append({
                "id": room['id'],
                "name": room['name'],
                "code": room['code'],
                "building": room['building'],
                "floor": room['floor'],
                "capacity": room['capacity'],
                "status": status,
                "type": room_type,
                "current_class": current_class,
                "schedules": schedules
            })
        
        return classroom_list
    
    all_classrooms = load_classrooms()
    
    def get_filtered_classrooms():
        """Filter classrooms based on search and filters"""
        filtered = all_classrooms.copy()
        
        # Search filter
        query = search_query["value"].lower().strip()
        if query:
            filtered = [r for r in filtered if 
                       query in r["name"].lower() or 
                       query in r["code"].lower() or 
                       query in r["building"].lower()]
        
        # Type filter
        if current_filters["type"] != "all":
            filtered = [r for r in filtered if r["type"] == current_filters["type"]]
        
        # Floor filter
        if current_filters["floor"] != "all":
            filtered = [r for r in filtered if r["floor"] == current_filters["floor"]]
        
        # Status filter
        if current_filters["status"] != "all":
            filtered = [r for r in filtered if r["status"] == current_filters["status"]]
        
        return filtered
    
    def get_status_color(status):
        return {
            "available": "#4CAF50",  # Green
            "occupied": "#F44336",   # Red
            "maintenance": "#FFC107" # Yellow
        }.get(status, c["text_secondary"])
    
    def get_status_text_color(status):
        return "#ffffff" if status != "maintenance" else "#000000"
    
    # ==================== SEARCH & FILTER HANDLERS ====================
    
    def on_search_change(e):
        search_query["value"] = e.control.value
        update_content()
    
    def on_type_filter_change(e):
        current_filters["type"] = e.control.value
        update_content()
    
    def on_floor_filter_change(e):
        current_filters["floor"] = e.control.value
        update_content()
    
    def on_status_filter_change(e):
        current_filters["status"] = e.control.value
        update_content()
    
    def on_view_change(view):
        current_view["value"] = view
        update_content()
    
    def update_content():
        """Update the main content based on current view and filters"""
        c = t()
        filtered = get_filtered_classrooms()
        
        if current_view["value"] == "list":
            content = build_list_view(filtered)
        else:
            content = build_schedule_view()
        
        content_container.current.content = content
        page.update()
    
    # ==================== SET CLASS DIALOG ====================
    
    def show_set_class_dialog(room):
        """Show dialog for instructors to set up a class schedule"""
        c = t()
        subject_field = ft.Ref[ft.TextField]()
        day_dropdown = ft.Ref[ft.Dropdown]()
        start_time_dropdown = ft.Ref[ft.Dropdown]()
        end_time_dropdown = ft.Ref[ft.Dropdown]()
        semester_dropdown = ft.Ref[ft.Dropdown]()
        section_field = ft.Ref[ft.TextField]()
        error_text = ft.Ref[ft.Text]()
        availability_text = ft.Ref[ft.Text]()
        
        # Day options
        day_options = [
            ft.dropdown.Option("Monday", "Monday"),
            ft.dropdown.Option("Tuesday", "Tuesday"),
            ft.dropdown.Option("Wednesday", "Wednesday"),
            ft.dropdown.Option("Thursday", "Thursday"),
            ft.dropdown.Option("Friday", "Friday"),
            ft.dropdown.Option("Saturday", "Saturday"),
        ]
        
        # Time options
        time_options = []
        for hour in range(7, 21):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                display = f"{hour:02d}:{minute:02d}"
                if hour < 12:
                    display += " AM"
                elif hour == 12:
                    display += " PM"
                else:
                    display = f"{hour-12:02d}:{minute:02d} PM"
                time_options.append(ft.dropdown.Option(time_str, display))
        
        # Semester options
        semester_options = [
            ft.dropdown.Option("1st Semester 2024-2025", "1st Semester 2024-2025"),
            ft.dropdown.Option("2nd Semester 2024-2025", "2nd Semester 2024-2025"),
            ft.dropdown.Option("Summer 2025", "Summer 2025"),
        ]
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def check_availability(e=None):
            """Check if the room is available at the selected time"""
            day = day_dropdown.current.value
            start = start_time_dropdown.current.value
            end = end_time_dropdown.current.value
            
            if not all([day, start, end]):
                availability_text.current.value = ""
                availability_text.current.visible = False
                page.update()
                return
            
            # Check for conflicts on the selected day
            # For demo, we'll check today's date - in real app, check all semester dates
            from datetime import datetime
            today = datetime.now()
            # Find next occurrence of selected day
            days_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
            target_day = days_map.get(day, 0)
            days_ahead = target_day - today.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_date = today + timedelta(days=days_ahead)
            date_str = next_date.strftime("%Y-%m-%d")
            
            has_conflict = db.check_schedule_conflict(room['id'], date_str, start, end)
            
            if has_conflict:
                availability_text.current.value = "⚠️ Room is OCCUPIED at this time"
                availability_text.current.color = c["error"]
            else:
                availability_text.current.value = "✓ Room is AVAILABLE at this time"
                availability_text.current.color = c["success"]
            
            availability_text.current.visible = True
            page.update()
        
        def set_class(e):
            subject = subject_field.current.value.strip()
            day = day_dropdown.current.value
            start_time = start_time_dropdown.current.value
            end_time = end_time_dropdown.current.value
            semester = semester_dropdown.current.value
            section = section_field.current.value.strip() if section_field.current.value else ""
            
            if not subject:
                error_text.current.value = "Please enter a subject name"
                error_text.current.visible = True
                page.update()
                return
            
            if not day:
                error_text.current.value = "Please select a day"
                error_text.current.visible = True
                page.update()
                return
            
            if not start_time or not end_time:
                error_text.current.value = "Please select start and end time"
                error_text.current.visible = True
                page.update()
                return
            
            if start_time >= end_time:
                error_text.current.value = "End time must be after start time"
                error_text.current.visible = True
                page.update()
                return
            
            # Calculate date for the selected day
            from datetime import datetime
            today = datetime.now()
            days_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
            target_day = days_map.get(day, 0)
            days_ahead = target_day - today.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_date = today + timedelta(days=days_ahead)
            date_str = next_date.strftime("%Y-%m-%d")
            
            # Check availability before setting
            if db.check_schedule_conflict(room['id'], date_str, start_time, end_time):
                error_text.current.value = "Room is occupied at this time. Please choose a different slot."
                error_text.current.visible = True
                page.update()
                return
            
            # Create schedule with day info in notes
            notes = f"Day: {day} | Semester: {semester or 'Not specified'}"
            if section:
                notes += f" | Section: {section}"
            
            schedule_id = db.create_room_schedule(
                room_id=room['id'], instructor_id=user_id,
                subject_name=subject, schedule_date=date_str,
                start_time=start_time, end_time=end_time, notes=notes
            )
            
            if schedule_id:
                dialog.open = False
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Class scheduled in {room['name']} on {day}s!"),
                    bgcolor=c["success"],
                )
                page.snack_bar.open = True
                # Refresh data
                nonlocal all_classrooms
                all_classrooms = load_classrooms()
                update_content()
            else:
                error_text.current.value = "Failed to set class schedule"
                error_text.current.visible = True
                page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.SCHOOL, color=c["accent"], size=24),
                    ft.Text("Set Class Schedule", size=16, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                ], spacing=8),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_color=c["text_secondary"], on_click=close_dialog),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(
                content=ft.Column([
                    # Room info
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.MEETING_ROOM, size=20, color=c["accent"]),
                            ft.Column([
                                ft.Text(room['name'], size=14, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                                ft.Text(f"{room['code']} • {room['building']} • {room['floor']} Floor", size=11, color=c["text_secondary"]),
                            ], spacing=0, expand=True),
                            ft.Container(
                                content=ft.Text(room['status'].upper(), size=9, 
                                    color="#ffffff" if room['status'] == "available" else "#000000",
                                    weight=ft.FontWeight.W_600),
                                bgcolor=get_status_color(room['status']),
                                padding=ft.padding.symmetric(horizontal=8, vertical=3), border_radius=10,
                            ),
                        ], spacing=10),
                        bgcolor=c["accent_bg"], padding=12, border_radius=8,
                    ),
                    
                    ft.Text("", ref=error_text, size=12, color=c["error"], visible=False),
                    ft.Text("", ref=availability_text, size=12, visible=False),
                    
                    ft.TextField(
                        ref=subject_field, label="Subject / Course Name",
                        hint_text="e.g., CC 101 - Introduction to Computing",
                        border_color=c["border"], focused_border_color=c["accent"],
                        hint_style=ft.TextStyle(color=c["text_hint"]), 
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        cursor_color=c["accent"], border_radius=8,
                    ),
                    
                    ft.TextField(
                        ref=section_field, label="Section (Optional)",
                        hint_text="e.g., BSCS 3A",
                        border_color=c["border"], focused_border_color=c["accent"],
                        hint_style=ft.TextStyle(color=c["text_hint"]), 
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        cursor_color=c["accent"], border_radius=8,
                    ),
                    
                    ft.Dropdown(
                        ref=semester_dropdown, label="Semester",
                        value="1st Semester 2024-2025",
                        options=semester_options, border_color=c["border"],
                        focused_border_color=c["accent"], 
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        border_radius=8,
                    ),
                    
                    ft.Dropdown(
                        ref=day_dropdown, label="Day of Week",
                        options=day_options, border_color=c["border"],
                        focused_border_color=c["accent"], 
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        border_radius=8, on_change=check_availability,
                    ),
                    
                    ft.Row([
                        ft.Dropdown(
                            ref=start_time_dropdown, label="Start Time",
                            options=time_options, border_color=c["border"],
                            focused_border_color=c["accent"], 
                            text_style=ft.TextStyle(color=c["text_primary"]),
                            label_style=ft.TextStyle(color=c["text_secondary"]),
                            border_radius=8, width=135, on_change=check_availability,
                        ),
                        ft.Dropdown(
                            ref=end_time_dropdown, label="End Time",
                            options=time_options, border_color=c["border"],
                            focused_border_color=c["accent"], 
                            text_style=ft.TextStyle(color=c["text_primary"]),
                            label_style=ft.TextStyle(color=c["text_secondary"]),
                            border_radius=8, width=135, on_change=check_availability,
                        ),
                    ], spacing=10),
                ], spacing=10, scroll=ft.ScrollMode.AUTO),
                width=300, height=420,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog, style=ft.ButtonStyle(color=c["text_secondary"])),
                ft.ElevatedButton("Set Class", bgcolor=c["accent"], color="#ffffff",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=set_class),
            ],
            actions_alignment=ft.MainAxisAlignment.END, 
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== EDIT SCHEDULE DIALOG (for instructors) ====================
    
    def show_edit_schedule_dialog(room, current_class):
        """Show dialog for instructors to edit their room schedule"""
        c = t()
        subject_field = ft.Ref[ft.TextField]()
        date_field = ft.Ref[ft.TextField]()
        start_time_dropdown = ft.Ref[ft.Dropdown]()
        end_time_dropdown = ft.Ref[ft.Dropdown]()
        notes_field = ft.Ref[ft.TextField]()
        error_text = ft.Ref[ft.Text]()
        
        schedule_id = current_class.get("schedule_id")
        
        time_options = []
        for hour in range(7, 21):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                display = f"{hour:02d}:{minute:02d}"
                if hour < 12:
                    display += " AM"
                elif hour == 12:
                    display += " PM"
                else:
                    display = f"{hour-12:02d}:{minute:02d} PM"
                time_options.append(ft.dropdown.Option(time_str, display))
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def update_schedule(e):
            subject = subject_field.current.value.strip()
            date = date_field.current.value.strip()
            start_time = start_time_dropdown.current.value
            end_time = end_time_dropdown.current.value
            notes = notes_field.current.value.strip() if notes_field.current.value else ""
            
            if not subject:
                error_text.current.value = "Please enter a subject name"
                error_text.current.visible = True
                page.update()
                return
            
            if not date:
                error_text.current.value = "Please enter a date"
                error_text.current.visible = True
                page.update()
                return
            
            if not start_time or not end_time:
                error_text.current.value = "Please select start and end time"
                error_text.current.visible = True
                page.update()
                return
            
            if start_time >= end_time:
                error_text.current.value = "End time must be after start time"
                error_text.current.visible = True
                page.update()
                return
            
            # Update the schedule in database
            success = db.update_room_schedule(
                schedule_id=schedule_id,
                subject_name=subject, schedule_date=date,
                start_time=start_time, end_time=end_time, notes=notes
            )
            
            if success:
                dialog.open = False
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Schedule updated successfully!"),
                    bgcolor=c["success"],
                )
                page.snack_bar.open = True
                # Refresh data
                nonlocal all_classrooms
                all_classrooms = load_classrooms()
                update_content()
            else:
                error_text.current.value = "Failed to update schedule"
                error_text.current.visible = True
                page.update()
        
        def delete_schedule(e):
            success = db.delete_room_schedule(schedule_id)
            if success:
                dialog.open = False
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Schedule deleted"),
                    bgcolor=c["warning"],
                )
                page.snack_bar.open = True
                nonlocal all_classrooms
                all_classrooms = load_classrooms()
                update_content()
        
        today = datetime.now().strftime("%Y-%m-%d")
        current_time = current_class.get("time", "").split(" - ")
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.EDIT_CALENDAR, color=c["warning"], size=24),
                    ft.Text("Edit Schedule", size=18, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                ], spacing=8),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_color=c["text_secondary"], on_click=close_dialog),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.MEETING_ROOM, size=20, color=c["accent"]),
                            ft.Column([
                                ft.Text(room['name'], size=14, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                                ft.Text(f"{room['code']} • {room['building']}", size=11, color=c["text_secondary"]),
                            ], spacing=0, expand=True),
                        ], spacing=10),
                        bgcolor=c["accent_bg"], padding=12, border_radius=8,
                    ),
                    ft.Text("", ref=error_text, size=12, color=c["error"], visible=False),
                    ft.TextField(
                        ref=subject_field, value=current_class.get("name", ""),
                        label="Subject / Class Name",
                        border_color=c["border"], focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        cursor_color=c["accent"], border_radius=8,
                    ),
                    ft.TextField(
                        ref=date_field, value=today, label="Date",
                        hint_text="YYYY-MM-DD",
                        border_color=c["border"], focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        cursor_color=c["accent"], border_radius=8,
                    ),
                    ft.Row([
                        ft.Dropdown(
                            ref=start_time_dropdown, label="Start Time",
                            value=current_time[0] if len(current_time) > 0 else None,
                            options=time_options, border_color=c["border"],
                            focused_border_color=c["accent"], 
                            text_style=ft.TextStyle(color=c["text_primary"]),
                            label_style=ft.TextStyle(color=c["text_secondary"]),
                            border_radius=8, width=135,
                        ),
                        ft.Dropdown(
                            ref=end_time_dropdown, label="End Time",
                            value=current_time[1] if len(current_time) > 1 else None,
                            options=time_options, border_color=c["border"],
                            focused_border_color=c["accent"], 
                            text_style=ft.TextStyle(color=c["text_primary"]),
                            label_style=ft.TextStyle(color=c["text_secondary"]),
                            border_radius=8, width=135,
                        ),
                    ], spacing=10),
                    ft.TextField(
                        ref=notes_field, label="Notes (Optional)",
                        multiline=True, min_lines=2, max_lines=3,
                        border_color=c["border"], focused_border_color=c["accent"],
                        text_style=ft.TextStyle(color=c["text_primary"]),
                        label_style=ft.TextStyle(color=c["text_secondary"]),
                        cursor_color=c["accent"], border_radius=8,
                    ),
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                width=300, height=400,
            ),
            actions=[
                ft.TextButton("Delete", on_click=delete_schedule, 
                             style=ft.ButtonStyle(color=c["error"])),
                ft.TextButton("Cancel", on_click=close_dialog, 
                             style=ft.ButtonStyle(color=c["text_secondary"])),
                ft.ElevatedButton("Update", bgcolor=c["accent"], color="#ffffff",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), 
                    on_click=update_schedule),
            ],
            actions_alignment=ft.MainAxisAlignment.END, 
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== ROOM DETAILS DIALOG ====================
    
    def show_room_details(room):
        """Show room details with schedules"""
        c = t()
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        schedules = room.get("schedules", [])
        
        schedule_list = [
            ft.Container(
                content=ft.Row([
                    ft.Container(width=3, height=36, bgcolor=c["accent"], border_radius=2),
                    ft.Column([
                        ft.Text(sched['subject_name'], size=12, weight=ft.FontWeight.W_500, color=c["text_primary"]),
                        ft.Text(f"{sched['start_time']} - {sched['end_time']}", size=10, color=c["text_secondary"]),
                    ], spacing=1, expand=True),
                ], spacing=8),
                bgcolor=c["bg_primary"], padding=8, border_radius=6,
            ) for sched in schedules
        ]
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.MEETING_ROOM, size=20, color=c["accent"]),
                        width=36, height=36, bgcolor=c["accent_bg"], border_radius=8,
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(room["name"], size=18, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                ], spacing=10),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_color=c["text_secondary"], on_click=close_dialog),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(
                content=ft.Column([
                    # Room info
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Room Code:", size=12, color=c["text_secondary"], width=80),
                                ft.Text(room["code"], size=12, color=c["text_primary"], weight=ft.FontWeight.W_500),
                            ]),
                            ft.Row([
                                ft.Text("Building:", size=12, color=c["text_secondary"], width=80),
                                ft.Text(room["building"], size=12, color=c["text_primary"]),
                            ]),
                            ft.Row([
                                ft.Text("Floor:", size=12, color=c["text_secondary"], width=80),
                                ft.Text(f"{room['floor']} Floor", size=12, color=c["text_primary"]),
                            ]),
                            ft.Row([
                                ft.Text("Capacity:", size=12, color=c["text_secondary"], width=80),
                                ft.Text(f"{room['capacity']} persons", size=12, color=c["text_primary"]),
                            ]),
                            ft.Row([
                                ft.Text("Type:", size=12, color=c["text_secondary"], width=80),
                                ft.Text(room.get("type", "lecture").capitalize(), size=12, color=c["text_primary"]),
                            ]),
                            ft.Row([
                                ft.Text("Status:", size=12, color=c["text_secondary"], width=80),
                                ft.Container(
                                    content=ft.Text(room["status"].capitalize(), size=10,
                                        color=get_status_text_color(room["status"]), weight=ft.FontWeight.W_600),
                                    bgcolor=get_status_color(room["status"]),
                                    padding=ft.padding.symmetric(horizontal=10, vertical=3), border_radius=10,
                                ),
                            ]),
                        ], spacing=6),
                        bgcolor=c["bg_primary"], padding=12, border_radius=8,
                    ),
                    ft.Container(height=12),
                    ft.Text("Today's Schedule", size=13, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                    ft.Container(height=4),
                    ft.Column(schedule_list, spacing=6) if schedule_list else 
                    ft.Container(
                        content=ft.Text("No classes scheduled today", size=12, color=c["text_secondary"], 
                                       text_align=ft.TextAlign.CENTER),
                        padding=20, alignment=ft.alignment.center,
                    ),
                ], spacing=4, scroll=ft.ScrollMode.AUTO),
                width=300, height=340,
            ),
            actions=[
                ft.TextButton("Close", on_click=close_dialog, style=ft.ButtonStyle(color=c["text_secondary"])),
                ft.ElevatedButton("Set Class", bgcolor=c["accent"], color="#ffffff",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=lambda e: (close_dialog(e), show_set_class_dialog(room)),
                    visible=is_instructor and room["status"] == "available",
                ),
            ],
            bgcolor=c["bg_card"], shape=ft.RoundedRectangleBorder(radius=16),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # ==================== LIST VIEW ====================
    
    def build_classroom_card(room):
        c = t()
        status = room["status"]
        current = room.get("current_class")
        
        status_badge = ft.Container(
            content=ft.Text(status.capitalize(), size=10, weight=ft.FontWeight.W_600,
                           color=get_status_text_color(status)),
            bgcolor=get_status_color(status),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            border_radius=12,
        )
        
        card_content = [
            ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.MEETING_ROOM, size=18, color=c["accent"]),
                        width=32, height=32, bgcolor=c["accent_bg"], border_radius=8,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column([
                        ft.Text(room["name"], size=14, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                        ft.Text(room["code"], size=11, color=c["text_secondary"]),
                    ], spacing=0, expand=True),
                ], spacing=10, expand=True),
                status_badge,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.BUSINESS, size=12, color=c["text_secondary"]),
                    ft.Text(room["building"], size=11, color=c["text_secondary"]),
                ], spacing=4),
                ft.Row([
                    ft.Icon(ft.Icons.LAYERS_OUTLINED, size=12, color=c["text_secondary"]),
                    ft.Text(f"{room['floor']} Floor", size=11, color=c["text_secondary"]),
                ], spacing=4),
                ft.Row([
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=12, color=c["text_secondary"]),
                    ft.Text(str(room['capacity']), size=11, color=c["text_secondary"]),
                ], spacing=4),
            ], spacing=12),
        ]
        
        # Current class indicator
        if current:
            card_content.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=3, height=36, bgcolor="#F44336", border_radius=2),
                        ft.Column([
                            ft.Text(current["name"], size=12, weight=ft.FontWeight.W_500, color="#F44336"),
                            ft.Text(current["time"], size=10, color=c["text_secondary"]),
                        ], spacing=1, expand=True),
                    ], spacing=10),
                    bgcolor=c["bg_secondary"], padding=10, border_radius=8,
                )
            )
        
        # Action buttons - responsive for all users
        buttons = []
        if is_instructor:
            # Instructors can set class schedules for available rooms or edit their schedules
            if status == "available":
                buttons.append(
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.ADD, size=14), ft.Text("Set Class", size=11)], spacing=4),
                        bgcolor=c["accent"], color="#ffffff", height=34,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            animation_duration=200,
                        ),
                        on_click=lambda e, r=room: show_set_class_dialog(r),
                    )
                )
            elif status == "occupied" and current and current.get("instructor") == f"{user.get('first_name', '')} {user.get('last_name', '')}":
                # Allow instructor to edit their own bookings
                buttons.append(
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.EDIT, size=14), ft.Text("Edit", size=11)], spacing=4),
                        bgcolor=c["warning"], color="#000000", height=34,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            animation_duration=200,
                        ),
                        on_click=lambda e, r=room: show_edit_schedule_dialog(r, current),
                    )
                )
        
        buttons.append(
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.VISIBILITY, size=14), ft.Text("Details", size=11)], spacing=4),
                bgcolor=c["bg_secondary"], color=c["text_primary"], height=34,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    animation_duration=200,
                ),
                on_click=lambda e, r=room: show_room_details(r),
            )
        )
        
        card_content.append(ft.Row(buttons, spacing=8, alignment=ft.MainAxisAlignment.END, wrap=True))
        
        return ft.Container(
            content=ft.Column(card_content, spacing=8),
            bgcolor=c["bg_card"], padding=14, border_radius=12,
            border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            on_click=lambda e, r=room: show_room_details(r),
            ink=True,
        )
    
    def build_list_view(rooms):
        c = t()
        if not rooms:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SEARCH_OFF, size=48, color=c["text_hint"]),
                    ft.Text("No rooms found", size=16, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                    ft.Text("Try adjusting your search or filters", size=12, color=c["text_secondary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.alignment.center, padding=40,
            )
        
        return ft.Column([
            build_classroom_card(room) for room in rooms
        ], spacing=10)
    
    # ==================== MAP VIEW (Floor Plan) ====================
    
    def build_map_view(rooms):
        c = t()
        
        # Group rooms by floor
        floors = {}
        for room in rooms:
            floor = room["floor"]
            if floor not in floors:
                floors[floor] = []
            floors[floor].append(room)
        
        def build_room_pin(room):
            status = room["status"]
            return ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(ft.Icons.MEETING_ROOM, size=16, 
                                       color="#ffffff" if status != "maintenance" else "#000000"),
                        width=32, height=32, bgcolor=get_status_color(status), border_radius=8,
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(room["code"], size=9, color=c["text_primary"], 
                           weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                on_click=lambda e, r=room: show_room_details(r),
                tooltip=f"{room['name']} - {status.capitalize()}",
            )
        
        def build_floor_section(floor_name, floor_rooms):
            # Sort rooms by code
            sorted_rooms = sorted(floor_rooms, key=lambda x: x['code'])
            
            return ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LAYERS, size=16, color=c["accent"]),
                            ft.Text(f"{floor_name} Floor", size=14, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                            ft.Text(f"({len(floor_rooms)} rooms)", size=12, color=c["text_secondary"]),
                        ], spacing=8),
                        margin=ft.margin.only(bottom=10),
                    ),
                    ft.Container(
                        content=ft.Row(
                            [build_room_pin(room) for room in sorted_rooms],
                            wrap=True, spacing=12, run_spacing=12,
                        ),
                        bgcolor=c["bg_secondary"], padding=16, border_radius=12,
                        border=ft.border.all(1, c["border"]),
                    ),
                ]),
                margin=ft.margin.only(bottom=16),
            )
        
        # Legend
        legend = ft.Container(
            content=ft.Row([
                ft.Row([ft.Container(width=12, height=12, bgcolor="#4CAF50", border_radius=3),
                       ft.Text("Available", size=10, color=c["text_secondary"])], spacing=4),
                ft.Row([ft.Container(width=12, height=12, bgcolor="#F44336", border_radius=3),
                       ft.Text("Occupied", size=10, color=c["text_secondary"])], spacing=4),
                ft.Row([ft.Container(width=12, height=12, bgcolor="#FFC107", border_radius=3),
                       ft.Text("Maintenance", size=10, color=c["text_secondary"])], spacing=4),
            ], spacing=16, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=c["bg_card"], padding=12, border_radius=8, margin=ft.margin.only(bottom=16),
            border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
        )
        
        if not floors:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.MAP_OUTLINED, size=48, color=c["text_hint"]),
                    ft.Text("No rooms to display", size=16, color=c["text_primary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.alignment.center, padding=40,
            )
        
        floor_sections = [legend]
        for floor in sorted(floors.keys()):
            floor_sections.append(build_floor_section(floor, floors[floor]))
        
        return ft.Column(floor_sections, spacing=0)
    
    # ==================== SCHEDULE VIEW ====================
    
    def build_schedule_view():
        c = t()
        today = datetime.now()
        
        def get_week_dates():
            start = today - timedelta(days=today.weekday())
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        
        def build_time_slot(time, schedules_at_time):
            slots = []
            for sched in schedules_at_time:
                room = next((r for r in all_classrooms if r['id'] == sched['room_id']), None)
                room_name = room['name'] if room else "Unknown"
                slots.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(sched['subject_name'], size=11, weight=ft.FontWeight.W_500, 
                                   color=c["text_primary"], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(room_name, size=9, color=c["text_secondary"]),
                        ], spacing=2),
                        bgcolor=c["accent_bg"], padding=8, border_radius=6, width=120,
                        border=ft.border.all(1, c["accent"]),
                    )
                )
            return slots if slots else [ft.Container(width=120)]
        
        # Daily view
        if schedule_view["value"] == "daily":
            date_str = selected_date["value"]
            all_schedules = []
            for room in all_classrooms:
                schedules = db.get_room_schedules(room['id'], date_str)
                for sched in schedules:
                    sched['room_id'] = room['id']
                    sched['room_name'] = room['name']
                all_schedules.extend(schedules)
            
            # Group by time
            time_slots = {}
            for sched in all_schedules:
                time_key = sched['start_time']
                if time_key not in time_slots:
                    time_slots[time_key] = []
                time_slots[time_key].append(sched)
            
            schedule_rows = []
            for hour in range(7, 21):
                time_key = f"{hour:02d}:00"
                time_display = f"{hour:02d}:00" if hour < 12 else f"{hour-12 if hour > 12 else 12}:00 PM"
                
                slots_at_time = time_slots.get(time_key, [])
                
                schedule_rows.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(time_display, size=11, color=c["text_secondary"], width=60),
                            ft.Container(width=1, height=40, bgcolor=c["border"]),
                            ft.Row(build_time_slot(time_key, slots_at_time), spacing=8, scroll=ft.ScrollMode.AUTO, expand=True),
                        ], spacing=8),
                        padding=ft.padding.symmetric(vertical=4),
                    )
                )
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_display = date_obj.strftime("%A, %B %d, %Y")
            
            return ft.Column([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_LEFT,
                        icon_color=c["text_primary"],
                        on_click=lambda e: change_date(-1),
                    ),
                    ft.Text(date_display, size=14, weight=ft.FontWeight.W_600, color=c["text_primary"], expand=True,
                           text_align=ft.TextAlign.CENTER),
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_RIGHT,
                        icon_color=c["text_primary"],
                        on_click=lambda e: change_date(1),
                    ),
                ]),
                ft.Container(height=8),
                ft.Column(schedule_rows, spacing=0, scroll=ft.ScrollMode.AUTO),
            ])
        
        # Weekly view
        else:
            week_dates = get_week_dates()
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            
            # Header row
            header = ft.Row([
                ft.Container(width=50),
                *[ft.Container(
                    content=ft.Column([
                        ft.Text(day_names[i], size=10, color=c["text_secondary"], text_align=ft.TextAlign.CENTER),
                        ft.Text(datetime.strptime(d, "%Y-%m-%d").strftime("%d"), size=12, 
                               color=c["text_primary"], weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    width=40, alignment=ft.alignment.center,
                ) for i, d in enumerate(week_dates)]
            ], spacing=2)
            
            return ft.Column([
                header,
                ft.Container(height=8),
                ft.Text("Weekly schedule view - showing current week", size=12, color=c["text_secondary"]),
            ])
    
    def change_date(delta):
        current = datetime.strptime(selected_date["value"], "%Y-%m-%d")
        new_date = current + timedelta(days=delta)
        selected_date["value"] = new_date.strftime("%Y-%m-%d")
        update_content()
    
    def toggle_schedule_view(view):
        schedule_view["value"] = view
        update_content()
    
    # ==================== STATS ====================
    
    available_count = len([r for r in all_classrooms if r["status"] == "available"])
    occupied_count = len([r for r in all_classrooms if r["status"] == "occupied"])
    maintenance_count = len([r for r in all_classrooms if r["status"] == "maintenance"])
    
    def build_stat_card(count, label, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(str(count), size=20, weight=ft.FontWeight.W_700, color=color),
                ft.Text(label, size=9, color=c["text_secondary"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=c["bg_card"], padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=10, expand=True,
            border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            ink=True,
        )
    
    # Get unique floors for filter
    unique_floors = sorted(set(r["floor"] for r in all_classrooms))
    floor_options = [ft.dropdown.Option("all", "All Floors")] + [
        ft.dropdown.Option(f, f"{f}") for f in unique_floors
    ]
    
    # ==================== BUILD PAGE ====================
    
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
                            ft.Text("CSPC", size=12, weight=ft.FontWeight.W_700, color=c["accent"]),
                            ft.Text("Room Locator", size=9, color=c["text_secondary"]),
                        ], spacing=0),
                    ], spacing=8),
                    ft.Container(
                        content=ft.Text(initials, size=12, weight=ft.FontWeight.W_600, color="#ffffff"),
                        width=32, height=32, bgcolor=c["accent"], border_radius=16,
                        alignment=ft.alignment.center,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ),
            
            # Welcome
            ft.Container(
                content=ft.Column([
                    ft.Text(f"Welcome, {user_name}", size=16, weight=ft.FontWeight.W_600, color=c["text_primary"]),
                    ft.Row([
                        ft.Text(student_id, size=11, color=c["text_secondary"]),
                        ft.Container(
                            content=ft.Text("Instructor" if is_instructor else "Student", size=9,
                                           color="#ffffff", weight=ft.FontWeight.W_600),
                            bgcolor=c["accent"] if is_instructor else c["info"],
                            padding=ft.padding.symmetric(horizontal=8, vertical=2), border_radius=10,
                        ),
                    ], spacing=8),
                ], spacing=2),
                margin=ft.margin.only(top=8, bottom=12),
            ),
            
            # Search bar
            ft.TextField(
                ref=search_field, hint_text="Search classrooms by name, code, or building...",
                prefix_icon=ft.Icons.SEARCH,
                on_change=on_search_change,
                border_color=c["border"], focused_border_color=c["accent"],
                hint_style=ft.TextStyle(color=c["text_hint"], size=12),
                text_style=ft.TextStyle(color=c["text_primary"]),
                cursor_color=c["accent"], border_radius=8,
                content_padding=ft.padding.symmetric(horizontal=10, vertical=10),
                height=42, bgcolor=c["bg_card"],
            ),
            
            ft.Container(height=10),
            
            # Filters row - responsive
            ft.ResponsiveRow([
                ft.Dropdown(
                    ref=type_dropdown, value="all",
                    options=[
                        ft.dropdown.Option("all", "All Types"),
                        ft.dropdown.Option("lecture", "Lecture"),
                        ft.dropdown.Option("laboratory", "Lab"),
                    ],
                    on_change=on_type_filter_change,
                    border_color=c["border"], focused_border_color=c["accent"],
                    text_style=ft.TextStyle(color=c["text_primary"], size=11),
                    border_radius=8, content_padding=8, dense=True,
                    col={"xs": 4, "sm": 4, "md": 4},
                ),
                ft.Dropdown(
                    ref=floor_dropdown, value="all",
                    options=floor_options,
                    on_change=on_floor_filter_change,
                    border_color=c["border"], focused_border_color=c["accent"],
                    text_style=ft.TextStyle(color=c["text_primary"], size=11),
                    border_radius=8, content_padding=8, dense=True,
                    col={"xs": 4, "sm": 4, "md": 4},
                ),
                ft.Dropdown(
                    ref=status_dropdown, value="all",
                    options=[
                        ft.dropdown.Option("all", "All"),
                        ft.dropdown.Option("available", "Available"),
                        ft.dropdown.Option("occupied", "Occupied"),
                    ],
                    on_change=on_status_filter_change,
                    border_color=c["border"], focused_border_color=c["accent"],
                    text_style=ft.TextStyle(color=c["text_primary"], size=11),
                    border_radius=8, content_padding=8, dense=True,
                    col={"xs": 4, "sm": 4, "md": 4},
                ),
            ], spacing=6),
            
            ft.Container(height=10),
            
            # Stats
            ft.Row([
                build_stat_card(available_count, "Available", "#4CAF50"),
                build_stat_card(occupied_count, "Occupied", "#F44336"),
                build_stat_card(maintenance_count, "Maintenance", "#FFC107"),
            ], spacing=8),
            
            ft.Container(height=12),
            
            # View toggle (List and Schedule only)
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LIST, size=16, 
                                   color=c["accent"] if current_view["value"] == "list" else c["text_secondary"]),
                            ft.Text("List", size=12, 
                                   color=c["accent"] if current_view["value"] == "list" else c["text_secondary"]),
                        ], spacing=4),
                        bgcolor=c["accent_bg"] if current_view["value"] == "list" else "transparent",
                        padding=ft.padding.symmetric(horizontal=16, vertical=8), border_radius=16,
                        on_click=lambda e: on_view_change("list"),
                        ink=True,
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_MONTH, size=16,
                                   color=c["accent"] if current_view["value"] == "schedule" else c["text_secondary"]),
                            ft.Text("Schedule", size=12,
                                   color=c["accent"] if current_view["value"] == "schedule" else c["text_secondary"]),
                        ], spacing=4),
                        bgcolor=c["accent_bg"] if current_view["value"] == "schedule" else "transparent",
                        padding=ft.padding.symmetric(horizontal=16, vertical=8), border_radius=16,
                        on_click=lambda e: on_view_change("schedule"),
                        ink=True,
                    ),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=c["bg_card"], padding=6, border_radius=20,
                border=ft.border.all(1, c["border"]) if page.theme_mode == ft.ThemeMode.LIGHT else None,
            ),
            
            ft.Container(height=12),
            
            # Main content
            ft.Container(
                ref=content_container,
                content=build_list_view(get_filtered_classrooms()),
                expand=True,
            ),
        ], scroll=ft.ScrollMode.AUTO, spacing=0),
        bgcolor=c["bg_primary"],
        expand=True,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
    )
