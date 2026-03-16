# Smart Classroom - Access Control System

A secure cross-platform classroom management application with **Access Control System** built with **Flet** (Python + Flutter rendering) for Camarines Sur Polytechnic Colleges (CSPC) - College of Computer Studies (CCS).

**Information Assurance Final Project** - Implements secure authentication, RBAC, and security controls.

![Platform](https://img.shields.io/badge/Platform-Desktop%20%7C%20Web%20%7C%20Mobile-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Flet](https://img.shields.io/badge/Flet-0.21+-purple)
![Security](https://img.shields.io/badge/Security-RBAC%20%7C%20Security%20Controls-red)

## 🎯 Project Overview

Smart Classroom Availability and Locator App for CCS is a comprehensive classroom management system designed for the College of Computer Studies at CSPC. It allows students to view room availability and helps instructors manage their class schedules and room bookings.

### Core Features

- 🔐 **User Authentication** - Secure login, registration, and password reset with CSPC email
- 🏫 **Classroom Management** - View all CCS building rooms across 4 floors
- 📅 **Room Scheduling** - Instructors can book and manage room schedules
- 🔍 **Room Search & Filters** - Search by name, code, building; filter by floor, type, status
- 📊 **Real-time Availability** - See which rooms are available, occupied, or under maintenance
- 💾 **Offline-First Storage** - SQLite database with sync capability
- 🎨 **Modern UI** - Beautiful, responsive interface with light/dark themes

### CCS Building Rooms

**1st Floor (Ground):**
- Lecture Room 1-6

**2nd Floor:**
- Faculty Room, Dean's Office, Repair Room, Mac Lab, Open Lab

**3rd Floor:**
- IT Lab 1, IT Lab 2, ERP Lab, CS Lab

**4th Floor:**
- Rise Lab, Research Room, LIS Lab, NAS Lab

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
│   ├── home.py            # Dashboard with room list
│   ├── activity.py        # Recent activity page
│   ├── schedule.py        # Class schedule page
│   ├── settings.py        # Settings & profile
│   └── admin.py           # Admin user management (RBAC)
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

2. **Install runtime dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. *(Optional)* **Install development dependencies (tests, linting, formatting):**
   ```bash
   pip install -r dev-requirements.txt
   ```

4. **Run the application:**
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

The **Admin** interface (User Management) is available only to users with the **Administrator** role. Open it from **Settings → Admin Panel → User Management**.

### What admins can do
- **User list** – View all users (admins, instructors, students) with search by name, student ID, or email
- **Create users** – Add new users and assign role (Student, Instructor, Administrator); password policy enforced
- **User details** – View profile, status, last login, failed attempts, and recent activity
- **Change role** – Change a user’s role (e.g. Student → Instructor, Instructor → Admin)
- **Account actions** – Enable or disable accounts; unlock locked accounts; reset passwords
- **Delete users** – Permanently remove users (with confirmation)
- **Responsive UI** – Admin page and dialogs work on mobile, tablet, and desktop

### Stats on the Admin page
- Total users, and counts by role (Admins, Instructors, Students) for a quick overview.

## 📋 User Flows

### 1. Authentication Flow
- Register new account (Student/Instructor)
- Students provide: Name, Email, Student ID, Course, Year, Password
- Instructors provide: Name, Email, Password (no Student ID required)
- Login with CSPC email
- Password reset via email verification

### 2. Room Browsing (All Users)
- View all CCS building rooms
- Search by room name, code, or building
- Filter by floor (1st-4th), type (Lecture/Lab), status (Available/Occupied)
- View room details and schedules

### 3. Room Booking (Instructor Only)
- Book available rooms for classes
- Set subject name, date, start/end time
- Edit or delete existing bookings
- System prevents scheduling conflicts

### 4. Schedule Management
- View daily schedule of all rooms
- Navigate between dates
- See which rooms are free at specific times

## 🔧 Technical Details

### State Management
Uses a simple observer pattern for reactive UI updates. Components subscribe to state changes and get notified automatically.

### Data Persistence
SQLite database with abstraction layer. Handles initialization, migrations, and graceful error recovery.

### Offline-First Strategy
Sync queue for operations when offline. Conflict resolution with multiple strategies.

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
- ✅ Clear problem-driven purpose (Classroom availability for CCS)
- ✅ 3+ core user flows
- ✅ Stateful UI with reactive updates
- ✅ Persistent data layer
- ✅ Error handling & validation
- ✅ Multi-page navigation
- ✅ Settings/configuration panel
- ✅ Theme support (Light/Dark mode)

### Enhancements Implemented
1. **Multi-platform deploy** - Desktop, Web, Mobile support
2. **Real-time room availability** - Live status updates
3. **Offline-first strategy** - SQLite with sync capability
4. **Responsive UI** - Works on all screen sizes

## 🆕 What's New in V2.0

This version upgrades the original V1 "it works" prototype into a more robust and showcase-ready release:

- **Robustness & Reliability**
  - Improved input validation across authentication, scheduling, and search flows
  - Friendlier error and feedback messages instead of raw error outputs
  - Better handling of empty states (no rooms, no schedules, no history)
  - Loading and progress indicators on long-running operations

- **UX & Polish**
  - More consistent layout, spacing, and color usage across all pages
  - Clear navigation between student, instructor, and admin views
  - Refined empty-state designs with guidance actions (e.g., set class, create schedule)
  - Responsive layout that works across common desktop and web viewports

- **Feature Depth**
  - Powerful room search and filtering (by floor, type, and status)
  - Enhanced classroom and schedule management for instructors
  - Additional feedback states (success, error, confirmation) on key actions
  - Strengthened data persistence with an improved SQLite layer

- **Developer Quality & Documentation**
  - Cleaner, more modular code structure (core, models, services, pages, components)
  - Expanded test suite (unit + integration + manual checklist)
  - Overhauled `README` with setup instructions, feature overview, and screenshots

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
