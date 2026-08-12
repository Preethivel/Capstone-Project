from flask import Blueprint, render_template, session
from ..models import Course, User, Enrollment

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    courses_count = Course.query.count()
    students_count = User.query.filter_by(role='learner').count()
    instructors_count = User.query.filter_by(role='instructor').count()
    
    return render_template('index.html', 
                         courses_count=courses_count,
                         students_count=students_count,
                         instructors_count=instructors_count)

@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        from flask import redirect, url_for, flash
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if user.role == 'instructor':
        return redirect(url_for('instructor.dashboard'))
    
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    
    total_courses = len(enrollments)
    completed_courses = sum(1 for e in enrollments if e.progress == 100)
    total_xp = user.xp
    
    return render_template('learner_dashboard.html', 
                         user=user, 
                         enrollments=enrollments,
                         total_courses=total_courses,
                         completed_courses=completed_courses,
                         total_xp=total_xp)

@main_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        from flask import redirect, url_for, flash
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

@main_bp.route('/enroll/<int:course_id>')
def enroll(course_id):
    from flask import redirect, url_for, flash, session
    from ..models import Enrollment, Course
    from ..app import db
    
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    course = Course.query.get_or_404(course_id)
    
    existing = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        flash('You are already enrolled in this course!', 'info')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    if course.price == 0:
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        db.session.add(enrollment)
        course.students += 1
        db.session.commit()
        flash(f'🎉 You have been enrolled in "{course.title}"!', 'success')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    return redirect(url_for('payment_page', course_id=course_id))

@main_bp.route('/payment/<int:course_id>')
def payment_page(course_id):
    from ..models import Course
    if 'user_id' not in session:
        from flask import redirect, url_for, flash
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    course = Course.query.get_or_404(course_id)
    return render_template('payment.html', course=course)

@main_bp.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    from flask import request, redirect, url_for, flash, session
    from ..models import Enrollment, Payment, Course
    from ..app import db
    from datetime import datetime
    
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    course_id = request.form.get('course_id')
    course = Course.query.get_or_404(course_id)
    
    payment = Payment(
        user_id=user_id,
        course_id=course_id,
        amount=course.price,
        status='completed',
        payment_method=request.form.get('payment_method', 'Manual'),
        completed_at=datetime.utcnow()
    )
    db.session.add(payment)
    
    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.session.add(enrollment)
    course.students += 1
    db.session.commit()
    
    flash(f'✅ Payment successful! You are now enrolled in "{course.title}"', 'success')
    return redirect(url_for('main.dashboard'))