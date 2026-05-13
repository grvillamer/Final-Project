# SpottEd - Manual Exploratory Test Checklist

## 1. Authentication Tests

### 1.1 Login Flow
- [ ] App displays splash screen on startup
- [ ] Splash screen navigates to login after 2.5 seconds
- [ ] Login form displays Student ID and Password fields
- [ ] Empty Student ID shows error message
- [ ] Empty Password shows error message
- [ ] Invalid credentials show error message
- [ ] Valid credentials navigate to home page
- [ ] "Forgot Password" link navigates to reset page
- [ ] "Register" link navigates to registration page

### 1.2 Registration Flow
- [ ] All required fields are present
- [ ] Empty Student ID shows validation error
- [ ] Invalid email format shows error
- [ ] Password less than 6 characters shows error
- [ ] Password mismatch shows error
- [ ] Successful registration navigates to home
- [ ] Duplicate email shows error
- [ ] Back button returns to login

### 1.3 Password Reset
- [ ] Email field accepts input
- [ ] Invalid email format shows error
- [ ] Non-existent email shows error
- [ ] Valid email shows password fields
- [ ] New password validation works
- [ ] Successful reset shows success message

## 2. Home Page Tests

### 2.1 Instructor View
- [ ] Welcome message displays user name
- [ ] Profile initials shown correctly
- [ ] "New Class" button visible
- [ ] "Take Attendance" button visible
- [ ] Stats cards show correct data
- [ ] Class list displays correctly
- [ ] "View All" navigates to classes page

### 2.2 Student View
- [ ] Welcome message displays user name
- [ ] "Scan QR Code" button visible
- [ ] Attendance rate displays correctly
- [ ] Enrolled classes shown
- [ ] Navigation to class details works

## 3. Class Management Tests

### 3.1 Create Class (Instructor)
- [ ] Form displays all fields
- [ ] Class code auto-generates
- [ ] Copy code button works
- [ ] Empty name shows error
- [ ] Successful creation navigates back
- [ ] New class appears in list

### 3.2 Edit Class
- [ ] Form pre-fills existing data
- [ ] Changes save correctly
- [ ] Cancel returns without saving

### 3.3 Delete Class
- [ ] Confirmation dialog appears
- [ ] Cancel keeps class
- [ ] Confirm removes class

### 3.4 Join Class (Student)
- [ ] Code input field works
- [ ] Invalid code shows error
- [ ] Valid code enrolls student
- [ ] Already enrolled shows message

## 4. Attendance Tests

### 4.1 Take Attendance (Instructor)
- [ ] Class selection works
- [ ] QR code displays
- [ ] Copy code button works
- [ ] Student list shows correctly
- [ ] Present/Late/Absent buttons work
- [ ] Stats update in real-time
- [ ] "Mark All Present" works

### 4.2 Mark Attendance (Student)
- [ ] QR scanner placeholder shows
- [ ] Manual code entry works
- [ ] Invalid code shows error
- [ ] Valid code marks present
- [ ] Recent attendance history displays

## 5. Analytics Tests

### 5.1 Instructor Analytics
- [ ] Class selector works
- [ ] Overview stats display
- [ ] AI prediction shows
- [ ] Trend indicator correct
- [ ] Risk level displays
- [ ] Recommendations show
- [ ] At-risk students list
- [ ] Student rankings display

### 5.2 Student Analytics
- [ ] Personal stats show
- [ ] Attendance breakdown correct
- [ ] Progress bar accurate
- [ ] By-class breakdown works
- [ ] Performance tip displays

## 6. Settings Tests

### 6.1 Profile
- [ ] User info displays correctly
- [ ] Edit profile button works
- [ ] First/Last name editable
- [ ] Email editable
- [ ] Student ID not editable
- [ ] Save updates successfully

### 6.2 Preferences
- [ ] Dark mode toggle works
- [ ] Notifications toggle works
- [ ] Settings persist after restart

### 6.3 Account
- [ ] Sign out confirmation shows
- [ ] Sign out returns to login

## 7. Navigation Tests

- [ ] Bottom navigation switches pages
- [ ] Back button works on sub-pages
- [ ] Navigation state persists
- [ ] No navigation on auth pages

## 8. Error Handling Tests

- [ ] Empty states display correctly
- [ ] Network errors handled (simulated)
- [ ] Invalid input caught
- [ ] Error messages are clear

## 9. Responsiveness Tests

- [ ] Desktop layout works
- [ ] Mobile layout works
- [ ] Web browser layout works
- [ ] Controls remain accessible

## 10. Data Persistence Tests

- [ ] Data survives app restart
- [ ] Settings persist
- [ ] Attendance records saved
- [ ] User session maintained (optional)

---

## Test Results Summary

| Category | Pass | Fail | Notes |
|----------|------|------|-------|
| Authentication | | | |
| Home Page | | | |
| Class Management | | | |
| Attendance | | | |
| Analytics | | | |
| Settings | | | |
| Navigation | | | |
| Error Handling | | | |
| Responsiveness | | | |
| Data Persistence | | | |

**Tester:** ________________
**Date:** ________________
**Platform:** ________________
**Notes:** ________________







