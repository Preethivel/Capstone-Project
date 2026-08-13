"""
Enrollment Service - Business logic for course enrollment
"""
from models import db, Enrollment, Course, Payment, User
from datetime import datetime

def check_enrollment(user_id, course_id):
    """Check if a user is enrolled in a course"""
    return Enrollment.query.filter_by(
        user_id=user_id, 
        course_id=course_id
    ).first() is not None

def enroll_free_course(user_id, course_id):
    """Enroll a user in a free course"""
    course = Course.query.get_or_404(course_id)
    
    existing = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        return False, "Already enrolled"
    
    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.session.add(enrollment)
    course.students += 1
    db.session.commit()
    return True, "Enrolled successfully"

def enroll_paid_course(user_id, course_id, payment_method='Manual'):
    """Enroll a user in a paid course"""
    course = Course.query.get_or_404(course_id)
    
    existing = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        return False, "Already enrolled"
    
    # Create payment record
    payment = Payment(
        user_id=user_id,
        course_id=course_id,
        amount=course.price,
        status='completed',
        payment_method=payment_method,
        completed_at=datetime.utcnow()
    )
    db.session.add(payment)
    
    # Create enrollment
    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.session.add(enrollment)
    course.students += 1
    db.session.commit()
    return True, "Payment successful, enrolled"

def get_user_enrollments(user_id):
    """Get all enrollments for a user"""
    return Enrollment.query.filter_by(user_id=user_id).all()

def update_progress(user_id, course_id, progress):
    """Update course progress for a user"""
    enrollment = Enrollment.query.filter_by(
        user_id=user_id, 
        course_id=course_id
    ).first_or_404()
    enrollment.progress = progress
    enrollment.last_accessed = datetime.utcnow()
    db.session.commit()
    return enrollment

def get_instructor_stats(instructor_id):
    """Get statistics for an instructor"""
    courses = Course.query.filter_by(instructor_id=instructor_id).all()
    
    total_courses = len(courses)
    total_students = sum(c.students for c in courses)
    total_revenue = 0
    
    for course in courses:
        enrollments = Enrollment.query.filter_by(course_id=course.id).all()
        total_revenue += len(enrollments) * course.price
    
    return {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_revenue': total_revenue,
        'courses': courses
    }