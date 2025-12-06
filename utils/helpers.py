"""
SpottEd Utility Functions
"""
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math


def generate_class_code(length: int = 6) -> str:
    """Generate a random class code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_qr_code(prefix: str = "SPOT") -> str:
    """Generate a unique QR code string"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"{prefix}-{timestamp}-{random_suffix}"


def format_date(date_str: str, format_type: str = "short") -> str:
    """Format date string for display"""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        if format_type == "short":
            return date.strftime("%b %d, %Y")
        elif format_type == "long":
            return date.strftime("%B %d, %Y at %I:%M %p")
        elif format_type == "time":
            return date.strftime("%I:%M %p")
        else:
            return date.strftime("%Y-%m-%d")
    except:
        return date_str


def time_ago(date_str: str) -> str:
    """Convert datetime to relative time string"""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - date
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
        else:
            return date.strftime("%b %d, %Y")
    except:
        return date_str


def get_initials(first_name: str, last_name: str) -> str:
    """Get initials from name"""
    first = first_name[0].upper() if first_name else ""
    last = last_name[0].upper() if last_name else ""
    return f"{first}{last}"


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))


def validate_cspc_email(email: str) -> bool:
    """Validate CSPC school email format"""
    import re
    # Accept emails ending with @cspc.edu.ph or any valid email for demo
    pattern = r'^[\w\.-]+@(cspc\.edu\.ph|[\w\.-]+\.\w+)$'
    return bool(re.match(pattern, email.lower()))


def is_cspc_email(email: str) -> bool:
    """Check if email is specifically a CSPC email"""
    return email.lower().endswith('@cspc.edu.ph')


def validate_student_id(student_id: str) -> bool:
    """Validate student ID format"""
    # Adjust pattern as needed for your institution
    return len(student_id) >= 4 and student_id.replace("-", "").replace("_", "").isalnum()


def calculate_attendance_rate(present: int, late: int, total: int) -> float:
    """Calculate attendance rate percentage"""
    if total == 0:
        return 0.0
    return round((present + late * 0.5) / total * 100, 1)


def get_attendance_status_color(rate: float) -> str:
    """Get color based on attendance rate"""
    if rate >= 90:
        return "#4CAF50"  # Green
    elif rate >= 75:
        return "#FFC107"  # Yellow
    elif rate >= 50:
        return "#FF9800"  # Orange
    else:
        return "#F44336"  # Red


def get_status_color(status: str) -> str:
    """Get color for attendance status"""
    colors = {
        "present": "#4CAF50",
        "late": "#FFC107",
        "absent": "#F44336",
        "excused": "#2196F3"
    }
    return colors.get(status.lower(), "#9E9E9E")


# ==================== AI ANALYTICS HELPERS ====================

def calculate_trend(data: List[float]) -> Tuple[str, float]:
    """Calculate trend direction and strength"""
    if len(data) < 2:
        return "stable", 0.0
    
    # Simple linear regression slope
    n = len(data)
    x_mean = (n - 1) / 2
    y_mean = sum(data) / n
    
    numerator = sum((i - x_mean) * (data[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return "stable", 0.0
    
    slope = numerator / denominator
    
    if slope > 0.5:
        return "improving", slope
    elif slope < -0.5:
        return "declining", slope
    else:
        return "stable", slope


def predict_attendance(history: List[Dict], days_ahead: int = 7) -> Dict:
    """Simple AI prediction for attendance"""
    if not history:
        return {
            "predicted_rate": 0,
            "confidence": 0,
            "trend": "unknown",
            "risk_level": "unknown"
        }
    
    # Extract attendance rates
    rates = []
    for record in history[-30:]:  # Last 30 sessions
        if record.get('total_students', 0) > 0:
            rate = record.get('present', 0) / record['total_students'] * 100
            rates.append(rate)
    
    if not rates:
        return {
            "predicted_rate": 0,
            "confidence": 0,
            "trend": "unknown",
            "risk_level": "unknown"
        }
    
    # Calculate statistics
    avg_rate = sum(rates) / len(rates)
    trend, slope = calculate_trend(rates)
    
    # Simple prediction (avg + trend adjustment)
    predicted = avg_rate + (slope * days_ahead)
    predicted = max(0, min(100, predicted))
    
    # Confidence based on data consistency
    if len(rates) >= 10:
        variance = sum((r - avg_rate) ** 2 for r in rates) / len(rates)
        std_dev = math.sqrt(variance)
        confidence = max(0, min(100, 100 - std_dev))
    else:
        confidence = len(rates) * 10
    
    # Risk assessment
    if predicted < 60:
        risk_level = "high"
    elif predicted < 75:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "predicted_rate": round(predicted, 1),
        "confidence": round(confidence, 1),
        "trend": trend,
        "risk_level": risk_level,
        "current_avg": round(avg_rate, 1)
    }


def identify_at_risk_students(students_data: List[Dict], threshold: float = 75.0) -> List[Dict]:
    """Identify students at risk of poor attendance"""
    at_risk = []
    
    for student in students_data:
        total = student.get('total_sessions', 0)
        if total == 0:
            continue
        
        present = student.get('present_count', 0)
        late = student.get('late_count', 0)
        rate = calculate_attendance_rate(present, late, total)
        
        if rate < threshold:
            at_risk.append({
                **student,
                'attendance_rate': rate,
                'risk_level': 'high' if rate < 50 else 'medium',
                'missed_sessions': total - present - late
            })
    
    # Sort by attendance rate (lowest first)
    at_risk.sort(key=lambda x: x['attendance_rate'])
    
    return at_risk


def generate_recommendations(analytics: Dict) -> List[str]:
    """Generate AI-powered recommendations based on analytics"""
    recommendations = []
    
    rate = analytics.get('overall_attendance_rate', 0)
    trend = analytics.get('trend', 'stable')
    
    if rate < 60:
        recommendations.append("⚠️ Critical: Attendance rate is very low. Consider mandatory attendance policies or engagement improvements.")
    elif rate < 75:
        recommendations.append("📊 Attention needed: Attendance could be improved. Try varying class activities or timing.")
    elif rate < 90:
        recommendations.append("👍 Good attendance overall. Minor improvements possible with incentive programs.")
    else:
        recommendations.append("🌟 Excellent attendance! Keep up the great engagement strategies.")
    
    if trend == "declining":
        recommendations.append("📉 Downward trend detected. Review recent changes that might be affecting attendance.")
    elif trend == "improving":
        recommendations.append("📈 Positive trend! Continue current strategies.")
    
    students_data = analytics.get('students_data', [])
    at_risk_count = len([s for s in students_data if s.get('present_count', 0) / max(s.get('total_sessions', 1), 1) < 0.75])
    
    if at_risk_count > 0:
        recommendations.append(f"👥 {at_risk_count} student(s) have attendance below 75%. Consider individual outreach.")
    
    return recommendations


def get_day_of_week_stats(sessions_data: List[Dict]) -> Dict[str, float]:
    """Analyze attendance by day of week"""
    day_stats = {
        'Monday': [], 'Tuesday': [], 'Wednesday': [],
        'Thursday': [], 'Friday': [], 'Saturday': [], 'Sunday': []
    }
    
    for session in sessions_data:
        try:
            date = datetime.fromisoformat(session['session_date'])
            day_name = date.strftime('%A')
            if session.get('total_students', 0) > 0:
                rate = session.get('present', 0) / session['total_students'] * 100
                day_stats[day_name].append(rate)
        except:
            continue
    
    # Calculate averages
    return {day: round(sum(rates)/len(rates), 1) if rates else 0 
            for day, rates in day_stats.items()}





