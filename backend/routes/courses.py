from flask import Blueprint, render_template, request, session
from ..models import Course, Enrollment

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

@courses_bp.route('/')
def list_courses():
    all_courses = Course.query.filter_by(status='approved').all()
    enrollments_count = 0
    if 'user_id' in session:
        enrollments_count = Enrollment.query.filter_by(user_id=session['user_id']).count()
    return render_template('courses.html', courses=all_courses, enrollments_count=enrollments_count)

@courses_bp.route('/<int:course_id>')
def detail(course_id):
    course = Course.query.get_or_404(course_id)
    is_enrolled = False
    if 'user_id' in session:
        is_enrolled = Enrollment.query.filter_by(
            user_id=session['user_id'], 
            course_id=course_id
        ).first() is not None
    return render_template('course_detail.html', course=course, is_enrolled=is_enrolled)