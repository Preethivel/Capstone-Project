from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import db, Course

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def is_admin():
    from flask import session
    return session.get('user_email') == 'admin@learnverse.com'

@admin_bp.route('/courses')
def courses():
    if not is_admin():
        flash('Admin access required!', 'danger')
        return redirect(url_for('main.index'))
    all_courses = Course.query.all()
    return render_template('admin_courses.html', courses=all_courses)

@admin_bp.route('/course/add', methods=['GET', 'POST'])
def add_course():
    if not is_admin():
        flash('Admin access required!', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        new_course = Course(
            title=request.form.get('title'),
            description=request.form.get('description'),
            domain=request.form.get('domain'),
            level=request.form.get('level'),
            price=float(request.form.get('price', 0)),
            instructor=request.form.get('instructor'),
            rating=0,
            students=0,
            status='approved'
        )
        db.session.add(new_course)
        db.session.commit()
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin.courses'))
    return render_template('add_course.html')

@admin_bp.route('/course/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    if not is_admin():
        flash('Admin access required!', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        course.title = request.form.get('title')
        course.description = request.form.get('description')
        course.domain = request.form.get('domain')
        course.level = request.form.get('level')
        course.price = float(request.form.get('price', 0))
        course.instructor = request.form.get('instructor')
        course.status = request.form.get('status')
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin.courses'))
    return render_template('edit_course.html', course=course)

@admin_bp.route('/course/delete/<int:course_id>')
def delete_course(course_id):
    if not is_admin():
        flash('Admin access required!', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin.courses'))