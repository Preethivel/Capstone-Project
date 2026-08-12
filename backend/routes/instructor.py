from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models import db, Course, Module, Lesson, Enrollment

instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')

def is_instructor():
    return session.get('user_role') == 'instructor'

@instructor_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    if not is_instructor():
        flash('Instructor access required!', 'danger')
        return redirect(url_for('main.index'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    courses = Course.query.filter_by(instructor_id=user_id).all()
    
    total_courses = len(courses)
    total_students = sum(c.students for c in courses)
    total_revenue = 0
    for course in courses:
        enrollments = Enrollment.query.filter_by(course_id=course.id).all()
        total_revenue += len(enrollments) * course.price
    
    return render_template('instructor_dashboard.html',
                         user=user,
                         courses=courses,
                         total_courses=total_courses,
                         total_students=total_students,
                         total_revenue=total_revenue)

@instructor_bp.route('/course/create', methods=['GET', 'POST'])
def create_course():
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    if not is_instructor():
        flash('Instructor access required!', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        new_course = Course(
            title=request.form.get('title'),
            description=request.form.get('description'),
            domain=request.form.get('domain'),
            level=request.form.get('level'),
            price=float(request.form.get('price', 0)),
            instructor=session['user_name'],
            instructor_id=session['user_id'],
            status='approved'
        )
        db.session.add(new_course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('instructor.dashboard'))
    
    return render_template('instructor_create_course.html')

# Add more instructor routes as needed...