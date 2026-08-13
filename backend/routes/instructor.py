"""
Instructor Routes - Course creation and management for instructors

This module handles instructor-only routes for creating and managing
courses, modules, and lessons.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Course, Module, Lesson
from services.course_service import get_course_by_id, create_course
from services.enrollment_service import get_instructor_stats

instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')


def is_instructor():
    """Check if current user is instructor based on role."""
    return session.get('user_role') == 'instructor'


@instructor_bp.route('/dashboard')
def dashboard():
    """
    Instructor dashboard showing courses and stats.
    
    Returns:
        Rendered instructor dashboard with course statistics
    """
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    if not is_instructor():
        flash('Instructor access required!', 'danger')
        return redirect(url_for('main.index'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    stats = get_instructor_stats(user_id)
    
    return render_template('instructor_dashboard.html',
                         user=user,
                         courses=stats['courses'],
                         total_courses=stats['total_courses'],
                         total_students=stats['total_students'],
                         total_revenue=stats['total_revenue'])


@instructor_bp.route('/course/create', methods=['GET', 'POST'])
def create_course():
    """
    Create a new course (instructor only).
    
    GET: Display create course form
    POST: Process course creation
    
    Returns:
        GET: Rendered create course form
        POST: Redirect to course details on success
    """
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    if not is_instructor():
        flash('Instructor access required!', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        course = create_course(request.form, session['user_id'], session['user_name'])
        flash('Course created successfully!', 'success')
        return redirect(url_for('instructor.course_details', course_id=course.id))
    
    return render_template('instructor_create_course.html')


@instructor_bp.route('/course/<int:course_id>')
def course_details(course_id):
    """
    Instructor view of course details with modules and lessons.
    
    Args:
        course_id: ID of the course to view
        
    Returns:
        Rendered course details page
    """
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    if not is_instructor():
        flash('Instructor access required!', 'danger')
        return redirect(url_for('main.index'))
    
    course = get_course_by_id(course_id)
    if course.instructor_id != session['user_id']:
        flash('You do not own this course!', 'danger')
        return redirect(url_for('instructor.dashboard'))
    
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.order).all()
    return render_template('instructor_course_details.html', course=course, modules=modules)


@instructor_bp.route('/course/<int:course_id>/module/add', methods=['GET', 'POST'])
def add_module(course_id):
    """
    Add a module to a course (instructor only).
    
    Args:
        course_id: ID of the course to add module to
        
    Returns:
        GET: Rendered add module form
        POST: Redirect to course details on success
    """
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    if not is_instructor():
        flash('Instructor access required!', 'danger')
        return redirect(url_for('main.index'))
    
    course = get_course_by_id(course_id)
    if course.instructor_id != session['user_id']:
        flash('You do not own this course!', 'danger')
        return redirect(url_for('instructor.dashboard'))
    
    if request.method == 'POST':
        module = Module(
            course_id=course_id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            order=Module.query.filter_by(course_id=course_id).count() + 1
        )
        db.session.add(module)
        db.session.commit()
        flash('Module added successfully!', 'success')
        return redirect(url_for('instructor.course_details', course_id=course_id))
    
    return render_template('instructor_add_module.html', course=course)


@instructor_bp.route('/module/<int:module_id>/lesson/add', methods=['GET', 'POST'])
def add_lesson(module_id):
    """
    Add a lesson to a module (instructor only).
    
    Args:
        module_id: ID of the module to add lesson to
        
    Returns:
        GET: Rendered add lesson form
        POST: Redirect to course details on success
    """
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    if not is_instructor():
        flash('Instructor access required!', 'danger')
        return redirect(url_for('main.index'))
    
    module = Module.query.get_or_404(module_id)
    course = Course.query.get(module.course_id)
    if course.instructor_id != session['user_id']:
        flash('You do not own this course!', 'danger')
        return redirect(url_for('instructor.dashboard'))
    
    if request.method == 'POST':
        lesson = Lesson(
            module_id=module_id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            video_url=request.form.get('video_url'),
            content=request.form.get('content'),
            order=Lesson.query.filter_by(module_id=module_id).count() + 1
        )
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson added successfully!', 'success')
        return redirect(url_for('instructor.course_details', course_id=course.id))
    
    return render_template('instructor_add_lesson.html', module=module, course=course)