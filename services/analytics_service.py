"""
Analytics Service - AI-Powered Attendance Analytics
Emerging Technology: Lightweight Data Analytics with Prediction
"""
from typing import List, Dict, Tuple, Optional
from database import db
from utils.helpers import (
    calculate_attendance_rate,
    calculate_trend,
    predict_attendance,
    identify_at_risk_students,
    generate_recommendations,
    get_day_of_week_stats
)


class AnalyticsService:
    """
    Service for AI-powered attendance analytics and insights.
    
    This implements the emerging technology requirement through:
    - Predictive analytics for attendance trends
    - Risk identification algorithms
    - Smart recommendation generation
    - Pattern recognition in attendance data
    """
    
    @staticmethod
    def get_class_analytics(class_id: int) -> Dict:
        """
        Get comprehensive analytics for a class.
        Returns detailed metrics, predictions, and recommendations.
        """
        raw_analytics = db.get_class_analytics(class_id)
        
        # AI Prediction
        prediction = predict_attendance(raw_analytics.get('sessions_data', []))
        
        # At-risk students identification
        at_risk = identify_at_risk_students(raw_analytics.get('students_data', []))
        
        # Generate AI recommendations
        recommendations = generate_recommendations({
            'overall_attendance_rate': raw_analytics.get('overall_attendance_rate', 0),
            'trend': prediction.get('trend', 'stable'),
            'students_data': raw_analytics.get('students_data', [])
        })
        
        # Day of week analysis
        day_stats = get_day_of_week_stats(raw_analytics.get('sessions_data', []))
        
        return {
            **raw_analytics,
            'prediction': prediction,
            'at_risk_students': at_risk,
            'recommendations': recommendations,
            'day_of_week_stats': day_stats,
        }
    
    @staticmethod
    def get_student_analytics(student_id: int) -> Dict:
        """Get analytics for a specific student"""
        return db.get_student_analytics(student_id)
    
    @staticmethod
    def get_attendance_prediction(class_id: int, days_ahead: int = 7) -> Dict:
        """
        AI-powered attendance prediction.
        Uses historical data to predict future attendance rates.
        """
        analytics = db.get_class_analytics(class_id)
        sessions_data = analytics.get('sessions_data', [])
        
        return predict_attendance(sessions_data, days_ahead)
    
    @staticmethod
    def get_at_risk_students(class_id: int, threshold: float = 75.0) -> List[Dict]:
        """
        Identify students at risk of poor attendance.
        Uses pattern recognition to flag students needing attention.
        """
        analytics = db.get_class_analytics(class_id)
        students_data = analytics.get('students_data', [])
        
        return identify_at_risk_students(students_data, threshold)
    
    @staticmethod
    def get_smart_recommendations(class_id: int) -> List[str]:
        """
        Generate AI-powered recommendations for improving attendance.
        Analyzes patterns and provides actionable insights.
        """
        analytics = db.get_class_analytics(class_id)
        prediction = predict_attendance(analytics.get('sessions_data', []))
        
        return generate_recommendations({
            'overall_attendance_rate': analytics.get('overall_attendance_rate', 0),
            'trend': prediction.get('trend', 'stable'),
            'students_data': analytics.get('students_data', [])
        })
    
    @staticmethod
    def get_trend_analysis(class_id: int) -> Dict:
        """
        Analyze attendance trends over time.
        Returns trend direction, strength, and insights.
        """
        analytics = db.get_class_analytics(class_id)
        sessions = analytics.get('sessions_data', [])
        
        if not sessions:
            return {
                'trend': 'unknown',
                'direction': 0,
                'insight': 'No attendance data available'
            }
        
        # Calculate rates for each session
        total_students = analytics.get('total_students', 1)
        rates = []
        
        for session in sessions:
            present = session.get('present', 0)
            rate = (present / total_students * 100) if total_students > 0 else 0
            rates.append(rate)
        
        trend, slope = calculate_trend(rates)
        
        insights = {
            'improving': f"Attendance is trending upward (+{abs(slope):.1f}% per session)",
            'declining': f"Attendance is trending downward ({slope:.1f}% per session)",
            'stable': "Attendance has been consistent"
        }
        
        return {
            'trend': trend,
            'direction': slope,
            'insight': insights.get(trend, 'Analyzing...')
        }
    
    @staticmethod
    def get_best_attendance_day(class_id: int) -> Tuple[str, float]:
        """Find the day of week with best attendance"""
        analytics = db.get_class_analytics(class_id)
        day_stats = get_day_of_week_stats(analytics.get('sessions_data', []))
        
        if not day_stats:
            return "Unknown", 0.0
        
        best_day = max(day_stats.items(), key=lambda x: x[1])
        return best_day
    
    @staticmethod
    def get_dashboard_metrics(user_id: int, is_instructor: bool) -> Dict:
        """Get dashboard metrics for home page"""
        if is_instructor:
            classes = db.get_classes_by_instructor(user_id)
            total_students = sum(c.get('student_count', 0) for c in classes)
            
            # Calculate average attendance across all classes
            total_rate = 0
            class_count = 0
            
            for cls in classes:
                analytics = db.get_class_analytics(cls['id'])
                if analytics.get('total_sessions', 0) > 0:
                    total_rate += analytics.get('overall_attendance_rate', 0)
                    class_count += 1
            
            avg_rate = total_rate / class_count if class_count > 0 else 0
            
            return {
                'total_classes': len(classes),
                'total_students': total_students,
                'avg_attendance_rate': round(avg_rate, 1),
                'recent_classes': classes[:5]
            }
        else:
            analytics = db.get_student_analytics(user_id)
            classes = db.get_enrolled_classes(user_id)
            
            return {
                'total_classes': analytics.get('total_classes', 0),
                'attendance_rate': analytics.get('overall_attendance_rate', 0),
                'present_count': analytics.get('present_count', 0),
                'total_sessions': analytics.get('total_sessions', 0),
                'enrolled_classes': classes[:5]
            }
    
    @staticmethod
    def export_analytics_report(class_id: int) -> Dict:
        """
        Generate exportable analytics report.
        Returns structured data suitable for CSV/PDF export.
        """
        analytics = AnalyticsService.get_class_analytics(class_id)
        class_info = db.get_class(class_id)
        
        return {
            'class_name': class_info.get('name', 'Unknown') if class_info else 'Unknown',
            'class_code': class_info.get('class_code', '') if class_info else '',
            'generated_at': __import__('datetime').datetime.now().isoformat(),
            'summary': {
                'total_sessions': analytics.get('total_sessions', 0),
                'total_students': analytics.get('total_students', 0),
                'overall_attendance_rate': analytics.get('overall_attendance_rate', 0),
            },
            'prediction': analytics.get('prediction', {}),
            'at_risk_count': len(analytics.get('at_risk_students', [])),
            'recommendations': analytics.get('recommendations', []),
            'sessions_data': analytics.get('sessions_data', []),
            'students_data': analytics.get('students_data', []),
        }







