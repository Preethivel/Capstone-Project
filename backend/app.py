from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_cors import CORS
from config import Config
from models import db, User, Course, Enrollment, Payment, Module, Lesson, LessonCompletion, Review

# ===== IMPORT SERVICES - FIXED =====
from services.course_service import get_all_courses, get_course_by_id, search_courses_service, get_course_stats
from services.enrollment_service import check_enrollment, enroll_free_course, get_user_enrollments, enroll_paid_course, get_instructor_stats

import os
from datetime import datetime
from collections import Counter
from flasgger import Swagger

# ===== CREATE DATABASE FOLDER =====
db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database')
os.makedirs(db_dir, exist_ok=True)

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config.from_object(Config)

# ===== CORS =====
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:5000", "http://localhost:5000"])

# ===== SWAGGER =====
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "LearnVerse API",
        "description": "AI-Powered Online Learning Platform",
        "version": "1.0.0",
        "contact": {
            "name": "Preethivel",
            "email": "preethivel@learnverse.com"
        }
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"]
})

db.init_app(app)

with app.app_context():
    db.create_all()
    print("✅ Database initialized successfully!")

# ==================== HELPERS ====================

def is_admin():
    return session.get('user_email') == 'admin@learnverse.com'

def is_instructor():
    return session.get('user_role') == 'instructor'

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def api_response(success=True, message="", data=None, status_code=200):
    response = {
        'success': success,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code

# ==================== AUTHENTICATION ====================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'learner')
        organization = request.form.get('organization', '')
        title = request.form.get('title', '')
        bio = request.form.get('bio', '')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('signup'))
        
        user = User(
            name=name, 
            email=email, 
            role=role,
            organization=organization,
            title=title,
            bio=bio
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_role'] = user.role
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))

# ==================== INDEX ====================

@app.route('/')
def index():
    courses_count = Course.query.count()
    students_count = User.query.filter_by(role='learner').count()
    instructors_count = User.query.filter_by(role='instructor').count()
    
    return render_template('index.html', 
                         courses_count=courses_count,
                         students_count=students_count,
                         instructors_count=instructors_count)

# ==================== COURSES ====================

@app.route('/courses')
def courses():
    all_courses = get_all_courses()
    enrollments_count = 0
    if 'user_id' in session:
        enrollments_count = len(get_user_enrollments(session['user_id']))
    return render_template('courses.html', courses=all_courses, enrollments_count=enrollments_count)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = get_course_by_id(course_id)
    is_enrolled = False
    if 'user_id' in session:
        is_enrolled = check_enrollment(session['user_id'], course_id)
    stats = get_course_stats(course_id)
    return render_template('course_detail.html', course=course, is_enrolled=is_enrolled, stats=stats)

# ==================== ENROLLMENT & PAYMENT ====================

@app.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    user_id = session['user_id']
    course = get_course_by_id(course_id)
    
    if check_enrollment(user_id, course_id):
        flash('You are already enrolled in this course!', 'info')
        return redirect(url_for('course_detail', course_id=course_id))
    
    if course.price == 0:
        success, message = enroll_free_course(user_id, course_id)
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return redirect(url_for('payment', course_id=course_id))

@app.route('/payment/<int:course_id>')
@login_required
def payment(course_id):
    course = get_course_by_id(course_id)
    return render_template('payment.html', course=course)

@app.route('/confirm_payment', methods=['POST'])
@login_required
def confirm_payment():
    user_id = session['user_id']
    course_id = request.form.get('course_id')
    payment_method = request.form.get('payment_method', 'Manual')
    
    success, message = enroll_paid_course(user_id, int(course_id), payment_method)
    flash(message, 'success' if success else 'danger')
    
    if success:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('payment', course_id=course_id))

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if user.role == 'instructor':
        return redirect(url_for('instructor_dashboard'))
    
    enrollments = get_user_enrollments(user_id)
    
    total_courses = len(enrollments)
    completed_courses = sum(1 for e in enrollments if e.progress == 100)
    total_xp = user.xp
    
    return render_template('learner_dashboard.html', 
                         user=user, 
                         enrollments=enrollments,
                         total_courses=total_courses,
                         completed_courses=completed_courses,
                         total_xp=total_xp)

@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

# ==================== INSTRUCTOR ====================

@app.route('/instructor/dashboard')
@login_required
def instructor_dashboard():
    user_id = session['user_id']
    user = User.query.get(user_id)
    stats = get_instructor_stats(user_id)
    
    return render_template('instructor_dashboard.html',
                         user=user,
                         courses=stats['courses'],
                         total_courses=stats['total_courses'],
                         total_students=stats['total_students'],
                         total_revenue=stats['total_revenue'])

@app.route('/instructor/course/create', methods=['GET', 'POST'])
@login_required
def instructor_create_course():
    from services.course_service import create_course
    
    if not is_instructor():
        flash('Instructor access required!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        course = create_course(request.form, session['user_id'], session['user_name'])
        flash('Course created successfully!', 'success')
        return redirect(url_for('instructor_course_details', course_id=course.id))
    
    return render_template('instructor_create_course.html')

@app.route('/instructor/course/<int:course_id>')
@login_required
def instructor_course_details(course_id):
    course = get_course_by_id(course_id)
    if course.instructor_id != session['user_id'] and not is_admin():
        flash('You do not have access to this course!', 'danger')
        return redirect(url_for('instructor_dashboard'))
    
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.order).all()
    return render_template('instructor_course_details.html', course=course, modules=modules)

@app.route('/instructor/course/<int:course_id>/module/add', methods=['GET', 'POST'])
@login_required
def instructor_add_module(course_id):
    course = get_course_by_id(course_id)
    if course.instructor_id != session['user_id']:
        flash('You do not own this course!', 'danger')
        return redirect(url_for('instructor_dashboard'))
    
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
        return redirect(url_for('instructor_course_details', course_id=course_id))
    
    return render_template('instructor_add_module.html', course=course)

@app.route('/instructor/module/<int:module_id>/lesson/add', methods=['GET', 'POST'])
@login_required
def instructor_add_lesson(module_id):
    module = Module.query.get_or_404(module_id)
    course = Course.query.get(module.course_id)
    if course.instructor_id != session['user_id']:
        flash('You do not own this course!', 'danger')
        return redirect(url_for('instructor_dashboard'))
    
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
        return redirect(url_for('instructor_course_details', course_id=course.id))
    
    return render_template('instructor_add_lesson.html', module=module, course=course)

# ==================== ADMIN ====================

@app.route('/admin/courses')
@login_required
def admin_courses():
    if not is_admin():
        flash('Admin access required!', 'danger')
        return redirect(url_for('index'))
    all_courses = Course.query.all()
    return render_template('admin_courses.html', courses=all_courses)

@app.route('/admin/course/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if not is_admin():
        flash('Admin access required!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        new_course = Course(
            title=request.form.get('title'),
            description=request.form.get('description'),
            domain=request.form.get('domain'),
            level=request.form.get('level'),
            price=float(request.form.get('price', 0)),
            instructor=request.form.get('instructor'),
            instructor_id=None,
            rating=0,
            students=0,
            status='approved'
        )
        db.session.add(new_course)
        db.session.commit()
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin_courses'))
    return render_template('add_course.html')

@app.route('/admin/course/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if not is_admin():
        flash('Admin access required!', 'danger')
        return redirect(url_for('index'))
    
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
        return redirect(url_for('admin_courses'))
    return render_template('edit_course.html', course=course)

@app.route('/admin/course/delete/<int:course_id>')
@login_required
def delete_course(course_id):
    if not is_admin():
        flash('Admin access required!', 'danger')
        return redirect(url_for('index'))
    
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin_courses'))

# ==================== API ====================

@app.route('/api/courses/search')
def search_courses():
    query = request.args.get('q', '')
    domain = request.args.get('domain', 'all')
    level = request.args.get('level', 'all')
    price = request.args.get('price', 'all')
    
    courses = search_courses_service(query, domain, level, price)
    
    result = [{
        'id': c.id,
        'title': c.title,
        'description': c.description[:100] + '...',
        'domain': c.domain,
        'level': c.level,
        'price': c.price,
        'instructor': c.instructor,
        'rating': c.rating,
        'students': c.students
    } for c in courses]
    
    return api_response(True, "Courses found", result, 200)

@app.route('/api/courses/recommend')
def recommend_courses():
    if 'user_id' not in session:
        popular = Course.query.filter_by(status='approved').order_by(Course.students.desc()).limit(4).all()
        result = [{
            'id': c.id,
            'title': c.title,
            'description': c.description[:100] + '...',
            'domain': c.domain,
            'level': c.level,
            'price': c.price,
            'instructor': c.instructor,
            'rating': c.rating,
            'students': c.students,
            'reason': '🔥 Popular among students'
        } for c in popular]
        return api_response(True, "Popular courses loaded", result, 200)
    
    user_id = session['user_id']
    enrolled = Enrollment.query.filter_by(user_id=user_id).all()
    enrolled_course_ids = [e.course_id for e in enrolled]
    
    if enrolled_course_ids:
        enrolled_courses = Course.query.filter(Course.id.in_(enrolled_course_ids)).all()
        domains = [c.domain for c in enrolled_courses]
        domain_counts = Counter(domains)
        top_domain = domain_counts.most_common(1)[0][0] if domain_counts else None
        
        if top_domain:
            recommended = Course.query.filter(
                Course.status == 'approved',
                Course.domain == top_domain,
                ~Course.id.in_(enrolled_course_ids)
            ).limit(4).all()
            
            if recommended:
                result = [{
                    'id': c.id,
                    'title': c.title,
                    'description': c.description[:100] + '...',
                    'domain': c.domain,
                    'level': c.level,
                    'price': c.price,
                    'instructor': c.instructor,
                    'rating': c.rating,
                    'students': c.students,
                    'reason': f'Based on your interest in {top_domain}'
                } for c in recommended]
                return api_response(True, "Personalized recommendations loaded", result, 200)
    
    popular = Course.query.filter_by(status='approved').order_by(Course.students.desc()).limit(4).all()
    result = [{
        'id': c.id,
        'title': c.title,
        'description': c.description[:100] + '...',
        'domain': c.domain,
        'level': c.level,
        'price': c.price,
        'instructor': c.instructor,
        'rating': c.rating,
        'students': c.students,
        'reason': '🔥 Popular among students'
    } for c in popular]
    return api_response(True, "Popular courses loaded", result, 200)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    return api_response(False, "Page not found", None, 404)

@app.errorhandler(500)
def internal_server_error(e):
    return api_response(False, "Internal server error", None, 500)

if __name__ == '__main__':
    app.run(debug=True, port=5000)