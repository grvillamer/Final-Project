# SpottEd (Smart Classroom) — Access Control System

**SpottEd** is a secure cross-platform classroom availability and locator app built with **Flet** (Python + Flutter rendering) for Camarines Sur Polytechnic Colleges (CSPC) — College of Computer Studies (CCS).

**Information Assurance Final Project** — Implements secure authentication, RBAC, audit logging, and security controls.

![Platform](https://img.shields.io/badge/Platform-Desktop%20%7C%20Web%20%7C%20Mobile-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Flet](https://img.shields.io/badge/Flet-0.21+-purple)
![Security](https://img.shields.io/badge/Security-RBAC%20%7C%20Security%20Controls-red)

## 🎯 Project Overview

SpottEd helps students find available classrooms across campus buildings and helps instructors set recurring class schedules per room. The app uses a **building-first** navigation flow: browse buildings on Home, open a building to see its rooms, then search or filter by floor.

### Core Features

- 🔐 **User Authentication** — Login, registration, and password reset with CSPC email validation
- 🏛️ **Building Directory** — Home lists campus buildings; tap a building to view its rooms
- 🗺️ **Campus Map** — Map tab with building search and quick navigation to room lists
- 📅 **Room Scheduling** — Instructors/admins set weekly recurring classes per room (semester-based)
- 📆 **Class Schedule** — Timetable view, QR attendance tab, and (for students) personal vs. official class sections
- 📜 **Activity History** — Recent actions; instructor recurring bookings show as **one consolidated entry**
- 🔍 **Room Search & Filters** — Search rooms by name/code; filter by floor within a building
- 📊 **Room Status** — Available, occupied, or under maintenance
- 💾 **Local Data** — SQLite with optional sync queue design; PostgreSQL migration planned for production
- 🎨 **Responsive UI** — Light/dark themes; desktop, web, and mobile layouts

### Bottom Navigation

| Tab | Purpose |
|-----|---------|
| **Home** | Building directory and room counts |
| **Map** | Campus map image + building search |
| **Activity** | Recent activity and booking history |
| **Schedule** | Timetable, QR attendance, personal schedule (students) |
| **Settings** | Profile, appearance, privacy, and app preferences |

### Campus Buildings (Home)

| Building | Seeded rooms (examples) |
|----------|-------------------------|
| **ACADEMIC BUILDING - I** | Classrooms ACAD 001–004 |
| **ACADEMIC BUILDING - II** | AB2 R001–R010 (1st); Pearl Function Hall, CSPC Travel Office, Laboratory (2nd); AB2 R011–R016 (3rd) |
| **ACADEMIC BUILDING - III** | AB3 R001–R005 (1st); Bloom/Bronfenbrenner/Bruner labs + L003–L004 (2nd); AB3 R006–R011 (3rd); CB 401–407 (4th) |
| **ACADEMIC BUILDING - IV** | Lecture rooms, labs, offices (multi-floor) |
| **ACADEMIC BUILDING - V** | *(rooms can be added via database seed)* |
| **GREEN BUILDING** | GB 101–105 (1st), GB 201–205 (2nd), GB 301–306 (3rd) |

Additional rooms (e.g. **CCS Building**) are initialized on first database setup. New building rooms are added automatically on startup when missing (`database.py` seed helpers).

## 📁 Project Structure

```
/Smart-Classroom-ACS
├── main.py                 # Application entry point
├── database.py             # SQLite database with security features
├── config.py               # Secure configuration loader
├── requirements.txt        # Python dependencies
├── env.example.txt         # Environment variable template
├── .gitignore             # Git ignore rules
├── README.md              # This file
│
├── /core                   # Security & Core Services
│   ├── security.py        # Password hashing, validation, policies
│   └── audit.py           # Audit logging service
│
├── /models                 # Data classes / DTOs
│   ├── user.py            # User model
│   ├── classroom.py       # Classroom and Schedule models
│   ├── attendance.py      # Attendance models
│   └── settings.py        # Settings model
│
├── /services              # Business logic layer
│   ├── auth_service.py    # Authentication service
│   ├── class_service.py   # Class management service
│   ├── attendance_service.py  # Attendance service
│   ├── analytics_service.py   # Analytics service
│   └── sync_service.py    # Offline sync service
│
├── /state                 # State management
│   ├── app_state.py       # Global application state
│   └── navigation_controller.py  # Navigation management
│
├── /pages                 # UI Views/Pages
│   ├── splash.py          # Splash screen
│   ├── login.py           # Login page
│   ├── register.py        # Registration page
│   ├── forgot_password.py # Password reset
│   ├── home.py            # Building directory (Home)
│   ├── building_rooms.py  # Rooms per building (search, floor filter, set class)
│   ├── map.py             # Campus map + building search
│   ├── activity.py        # Recent activity (consolidated instructor history)
│   ├── schedule.py        # Class schedule (timetable + QR attendance)
│   ├── room_schedule_dialogs.py  # Set class / recurring schedule dialog
│   ├── settings.py        # Settings & profile
│   ├── admin.py           # Admin user management (RBAC)
│   ├── audit_logs.py      # Security audit log viewer (admin)
│   ├── attendance.py      # Attendance views
│   ├── classes.py         # Class management pages
│   └── analytics.py       # Attendance analytics
│
├── /components            # Reusable UI components
│   ├── navigation.py      # Navigation components
│   └── cards.py           # Card components
│
├── /utils                 # Utility functions
│   ├── helpers.py         # Helper functions
│   └── theme.py           # Theme management (Light/Dark)
│
├── /logs                  # Log files (auto-created)
│   └── security.log       # Security-critical events
│
├── /tests                 # Test suite
│   ├── test_models.py     # Unit tests - Models
│   ├── test_services.py   # Unit tests - Services
│   ├── test_integration.py # Integration tests
│   └── test_checklist.md  # Manual test checklist
│
└── /assets               # Static assets (images, icons)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**

2. **Create a virtual environment (recommended on Windows):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install runtime dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. *(Optional)* **Install development dependencies (tests, linting, formatting):**
   ```bash
   pip install -r dev-requirements.txt
   ```

5. **Run the application:**
   ```bash
   flet run main.py
   ```

### Running on Different Platforms

The app is designed to work seamlessly on all platforms with responsive UI.

**Desktop (Windows/macOS/Linux):**
```bash
flet run main.py
```

**Web Browser (Website Mode):**
```bash
flet run main.py --web
```
Then open your browser to `http://localhost:8550`

To run on a specific port:
```bash
flet run main.py --web --port 8080
```

To make it accessible on your network (for testing on other devices):
```bash
flet run main.py --web --host 0.0.0.0 --port 8080
```
Then access from any device using `http://YOUR_IP:8080`

**Mobile (Android) - Development:**
```bash
flet run main.py --android
```
This opens the app in the Flet mobile app for testing.

**Mobile (iOS) - Development:**
```bash
flet run main.py --ios
```

### Building for Production

**Build Android APK:**
```bash
flet build apk
```

**Build iOS App:**
```bash
flet build ipa
```

**Build Web App (Static Files):**
```bash
flet build web
```
This creates a `build/web` folder with static files you can deploy to any web server.

**Deploy to Flet Cloud (Free):**
```bash
flet publish main.py
```
This gives you a public URL that works on both web and mobile browsers.

## 🧪 Testing

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Files
```bash
python -m pytest tests/test_models.py -v
python -m pytest tests/test_services.py -v
python -m pytest tests/test_integration.py -v
```

### Test Coverage

The test suite includes:
- **Unit Tests (10+)**: Models, Services, Utilities
- **Integration Tests (4)**: Complete user flows
- **Manual Test Checklist**: `tests/test_checklist.md`

## 👥 Demo Accounts

**Administrator (Full Access):**
- Student ID: `ADMIN001`
- Password: `Admin@123`
- Access: User Management and all features

**Instructor:**
- Student ID: `INST001`
- Password: `password123`
- Access: Room Booking, Class Management

**Student:**
- Student ID: `STU001`
- Password: `password123`
- Access: View Rooms, View Schedule

## 👤 About Admin

The **Admin** interface (User Management) is only available to users with the **Administrator** role (`pages/admin.py`). Administrators can also set room schedules like instructors.

### What the admin can do
- **User list** – View all users (admins, instructors, students); search by name, student ID, or email
- **Create users** – Add new users and assign role (Student, Instructor, Administrator); password policy enforced
- **User details** – View profile, status, last login, failed attempts, and recent activity
- **Change role** – Change a user’s role (e.g. Student → Instructor, Instructor → Admin)
- **Account actions** – Enable or disable accounts; unlock locked accounts; reset passwords
- **Delete users** – Permanently remove users (with confirmation)
- **Responsive UI** – Admin page and dialogs work on mobile, tablet, and desktop

### Stats on the Admin page
- **Total users** and counts by role (Admins, Instructors, Students) for a quick overview.

## 📋 User Flows

### 1. Authentication Flow
- Register new account (Student/Instructor)
- Students provide: Name, Email, Student ID, Course, Year, Password
- Instructors provide: Name, Email, Password (no Student ID required)
- Login with CSPC email
- Password reset via email verification

### 2. Building & Room Browsing (All Users)
- **Home** → select a building (e.g. Green Building, Academic Building II)
- **Building rooms** → search rooms, filter by floor, view status
- **Map** → search buildings and open the same room list

### 3. Room Scheduling (Instructor / Admin)
- Open a room → **Set Class**
- Choose subject, day, time, section, and semester
- System creates **weekly recurring** `room_schedules` for the semester
- Conflicting slots are skipped; success message shows how many sessions were created

### 4. Schedule Page
- **Timetable** — weekly grid of classes
- **QR Code** — instructors generate attendance codes; students scan or enter manually
- **Students** — separate **Scheduled Classes** and **My Personal Classes** sections; add personal blocks only visible to you

### 5. Activity (History)
- Shows recent logins, views, and instructor bookings
- Recurring class sets appear as **one activity card** (same room, subject, time, notes) with date range and session count — not one row per week

## 🔧 Technical Details

### State Management
Uses a simple observer pattern for reactive UI updates. Components subscribe to state changes and get notified automatically.

### Data Persistence
Current implementation uses SQLite for local development and testing.  
For production and centralized multi-user deployment, the system is being migrated to a client-server database (PostgreSQL recommended) with shared access through the backend service layer.

### Offline-First Strategy
Sync queue for operations when offline. Conflict resolution with multiple strategies.

## 🧾 Panel Recommendations and Actions

The panel recommended centralizing the database to improve data consistency, management, and efficiency across the system. They also noted that SQLite is not ideal for networked multi-user deployment.

### Our Response
- We agree with the recommendation and treat SQLite as a development-stage database.
- We will transition to a centralized relational database, with PostgreSQL as the primary target.
- Clients will access data through a service layer to enforce validation, access control, and audit logging consistently.

### Migration Plan
1. Prepare PostgreSQL schema equivalent to the current SQLite structure.
2. Create migration scripts to transfer existing records safely.
3. Move environment-based database configuration to support centralized deployment.
4. Validate data integrity and run multi-user concurrency tests.
5. Enable scheduled backups, role-based DB access, and monitoring.

### Security (Access Control System)

This application implements comprehensive security controls for the Information Assurance course:

#### 🔐 Authentication
- **Secure Password Hashing**: bcrypt with cost factor 12 (SHA-256 fallback)
- **Account Lockout**: 5 failed attempts triggers 15-minute lockout
- **Session Management**: Configurable timeout, secure token generation
- **Login Attempt Tracking**: Records all authentication attempts

#### 👥 Role-Based Access Control (RBAC)
- **Three Roles**: Admin, Instructor, Student
- **UI-Level Enforcement**: Components hidden based on role
- **Backend Enforcement**: All sensitive operations validate role
- **Default Admin**: System creates initial admin on first run

#### 📋 Password Policy
- Minimum 8 characters
- Requires uppercase, lowercase, digit, and special character
- Prevents password reuse (last 5 passwords)
- Blocks common/weak passwords
- Real-time strength indicator

#### 🛡️ Additional Security
- Input validation and sanitization
- Secure configuration via environment variables
- No hardcoded secrets in repository
- CSRF protection design

## ✅ Requirements Compliance

### Core Objectives
- ✅ Flet UI framework usage
- ✅ Data persistence (SQLite)
- ✅ Offline-first strategy
- ✅ Modular code structure
- ✅ Functional, usable interface

### Features
- ✅ Clear problem-driven purpose (Campus classroom availability for CSPC)
- ✅ 3+ core user flows (auth, building/room browse, schedule/attendance)
- ✅ Stateful UI with reactive updates
- ✅ Persistent data layer (SQLite; PostgreSQL migration planned)
- ✅ Error handling & validation
- ✅ Multi-page navigation with bottom nav + building drill-down
- ✅ Settings/configuration panel
- ✅ Theme support (Light/Dark mode)
- ✅ Campus map and multi-building room directory

### Enhancements Implemented
1. **Multi-platform deploy** - Desktop, Web, Mobile support
2. **Real-time room availability** - Live status updates
3. **Offline-first strategy** - SQLite with sync capability
4. **Responsive UI** - Works on all screen sizes

## 🆕 What's New in V2.0

This version upgrades the original V1 prototype into a more robust, campus-wide release:

- **Building-first navigation** — Home shows buildings; rooms open in `building_rooms.py`
- **Map tab** — Dedicated campus map page with building search
- **Expanded room database** — Green Building, Academic Building II & III (and more) seeded in `database.py`
- **Recurring semester scheduling** — One “Set Class” action creates weekly sessions for the full semester
- **Schedule UI** — Timetable + QR Code tabs; student personal vs. official schedules separated
- **Activity history** — Instructor recurring bookings consolidated into a single history entry
- **Panel-driven database plan** — SQLite for development; documented path to centralized PostgreSQL

- **Robustness & Reliability**
  - Improved validation across authentication, scheduling, and search
  - Clear empty states and snackbar feedback on actions
  - Conflict detection when booking rooms

- **UX & Polish**
  - Five-tab bottom navigation (Home, Map, Activity, Schedule, Settings)
  - Responsive layout for desktop, web, and mobile
  - Light/dark theme support

- **Developer Quality**
  - Modular pages (`building_rooms`, `room_schedule_dialogs`, `map`, etc.)
  - Unit + integration tests and manual checklist in `/tests`

### 🔒 Security Enhancements (Information Assurance Project)

**Selected Optional Features (3+):**

1. ✅ **Password Policy** (complexity, reuse prevention)
   - Minimum 8 characters with complexity requirements
   - Blocks common/weak passwords
   - Prevents reuse of last 5 passwords
   - Real-time strength indicator

2. ✅ **User Activity Monitoring** (last login, failed attempts)
   - Login history tracking
   - Failed attempt monitoring
   - Account lockout status
   - Activity timeline

**Baseline Security Features:**
- ✅ Secure login/logout with bcrypt hashing
- ✅ Account lockout (5 attempts / 15 min)
- ✅ RBAC with Admin, Instructor, Student roles
- ✅ User management (Admin only)
- ✅ Profile management with password change
- ✅ Session timeout handling
- ✅ Secure configuration (no hardcoded secrets)
- ✅ Comprehensive logging

### Testing
- ✅ 10+ unit tests (models, services)
- ✅ 4 integration tests (complete flows)
- ✅ Manual test checklist

## 👩‍💻 Team

**Section: BSCS 3B**

| Name | Role |
|------|------|
| Gracielle Ann Villamer | Developer |
| Feliah Hadassah Salvamante | Documentation & PPT |
| Marriet Jhoy Tagum | Documentation |

## 📝 License

MIT License - Feel free to use and modify for educational purposes.

## 🙏 Acknowledgments

- Built with [Flet](https://flet.dev/) framework
- Designed for Camarines Sur Polytechnic Colleges (CSPC)
- College of Computer Studies (CCS)
- CS 3110 / APPDEV Final Project

## 📸 SCREENSHOTS

---

## 🔐 SIGN UP PAGE
### Sign Up
![Sign Up](FP_screenshots/SignUp_Page.png)

---

## 🆕 CREATE ACCOUNT PAGE
### Student Account
![Student Account (Create)](FP_screenshots/Student_Acc..png)

### Admin / Instructor Account
![Instructor Account (Create)](FP_screenshots/Instructor_acc.png)

---

## 🎓 STUDENT ACCOUNT

### Home Page
![Student Home](FP_screenshots/Home_student.png)

### View Class
![View Class - Student](FP_screenshots/viewClass_student.png)

### History
![Student History](FP_screenshots/History_stud.png)

### Clear History
![Clear History - Student](FP_screenshots/clear_history.png)

### Schedule
![Student Schedule](FP_screenshots/sched_studenAcc.png)

### View Schedule List
![Student View Schedule List](FP_screenshots/viewsched_student.png)

### Attendance QR Code
![Attendance QR Code](FP_screenshots/attendance_code.png)

---

## 🧑‍🏫 INSTRUCTOR ACCOUNT

### Home Page
![Instructor Home](FP_screenshots/Homepage_Instructor.png)

### History
![Instructor History](FP_screenshots/history_instructor.png)

### Clear History
![Clear History - Instructor](FP_screenshots/clear_history.png)

### Search Room
![Search Room](FP_screenshots/search_bar.png)

### Set Class
![Set Class](FP_screenshots/setclass_page.png)

### View Schedule
![Instructor View Schedule](FP_screenshots/view_schedule.png)

### QR Code Generator
![Instructor QR Code](<FP_screenshots/qr_code instructor.png>)
---

## ⚙️ SETTINGS PAGE

### Edit Profile Information
![Edit Profile](FP_screenshots/Edit_ProfileInfo.png)

### Appearance & Settings
![Appearance Settings](FP_screenshots/Apperance_settings.png)

### Language & Notification
![Language & Notification](FP_screenshots/Language_notificatioSettings.png)

### Privacy & Security
![Privacy & Security](FP_screenshots/privacy_security.png)

### About App
![About App](FP_screenshots/about_app.png)

### Help & Support
![Help & Support](FP_screenshots/abt.App_Icon(1).png)

### Contact Developer
![Contact Developer](FP_screenshots/abt.App_Icon(2).png)

### Terms of Service
![Terms of Service](FP_screenshots/abt.App_Icon(3).png)

### Privacy Policy
![Privacy Policy](FP_screenshots/abt.App_Icon(4).png)

### Logging Out
![Logout](FP_screenshots/logging_out.png)

### Deleting Account
![Deleting Account](FP_screenshots/deleting_account.png)
