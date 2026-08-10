from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from config import Config
from models import db, User, Course, Enrollment, Payment, Module, Lesson, LessonCompletion, Review
import os
from datetime import datetime

# ===== CREATE DATABASE FOLDER =====
db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database')
os.makedirs(db_dir, exist_ok=True)

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config.from_object(Config)

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
    all_courses = Course.query.filter_by(status='approved').all()
    return render_template('courses.html', courses=all_courses)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    is_enrolled = False
    if 'user_id' in session:
        is_enrolled = Enrollment.query.filter_by(
            user_id=session['user_id'], 
            course_id=course_id
        ).first() is not None
    return render_template('course_detail.html', course=course, is_enrolled=is_enrolled)

# ==================== ENROLLMENT & PAYMENT ====================

@app.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    user_id = session['user_id']
    course = Course.query.get_or_404(course_id)
    
    existing = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        flash('You are already enrolled in this course!', 'info')
        return redirect(url_for('course_detail', course_id=course_id))
    
    if course.price == 0:
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        db.session.add(enrollment)
        course.students += 1
        db.session.commit()
        flash(f'🎉 You have been enrolled in "{course.title}"!', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return redirect(url_for('payment', course_id=course_id))

@app.route('/payment/<int:course_id>')
@login_required
def payment(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('payment.html', course=course)

@app.route('/confirm_payment', methods=['POST'])
@login_required
def confirm_payment():
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
    return redirect(url_for('dashboard'))

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if user.role == 'instructor':
        return redirect(url_for('instructor_dashboard'))
    
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

@app.route('/instructor/course/create', methods=['GET', 'POST'])
@login_required
def instructor_create_course():
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
        return redirect(url_for('instructor_dashboard'))
    
    return render_template('instructor_create_course.html')

@app.route('/instructor/course/<int:course_id>')
@login_required
def instructor_course_details(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != session['user_id'] and not is_admin():
        flash('You do not have access to this course!', 'danger')
        return redirect(url_for('instructor_dashboard'))
    
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.order).all()
    return render_template('instructor_course_details.html', course=course, modules=modules)

@app.route('/instructor/course/<int:course_id>/module/add', methods=['GET', 'POST'])
@login_required
def instructor_add_module(course_id):
    course = Course.query.get_or_404(course_id)
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

# ==================== REVIEWS ====================

@app.route('/course/<int:course_id>/review', methods=['POST'])
@login_required
def add_review(course_id):
    user_id = session['user_id']
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    
    existing = Review.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        flash('You have already reviewed this course!', 'warning')
        return redirect(url_for('course_detail', course_id=course_id))
    
    review = Review(
        user_id=user_id,
        course_id=course_id,
        rating=int(rating),
        comment=comment
    )
    db.session.add(review)
    
    course = Course.query.get(course_id)
    all_reviews = Review.query.filter_by(course_id=course_id).all()
    course.rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    db.session.commit()
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('course_detail', course_id=course_id))

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
@app.route('/api/courses/recommend')
def recommend_courses():
    """Simple AI recommendation based on user's enrolled courses"""
    if 'user_id' not in session:
        # Return popular courses for guest
        popular = Course.query.filter_by(status='approved').order_by(Course.students.desc()).limit(4).all()
        return jsonify([{
            'id': c.id,
            'title': c.title,
            'description': c.description[:100] + '...',
            'domain': c.domain,
            'level': c.level,
            'price': c.price,
            'instructor': c.instructor,
            'rating': c.rating,
            'students': c.students
        } for c in popular])
    
    # Get user's enrolled courses
    user_id = session['user_id']
    enrolled = Enrollment.query.filter_by(user_id=user_id).all()
    enrolled_course_ids = [e.course_id for e in enrolled]
    
    # Get domains user is interested in
    if enrolled_course_ids:
        enrolled_courses = Course.query.filter(Course.id.in_(enrolled_course_ids)).all()
        domains = [c.domain for c in enrolled_courses]
        
        # Recommend courses from same domains (excluding already enrolled)
        recommended = Course.query.filter(
            Course.status == 'approved',
            Course.domain.in_(domains),
            ~Course.id.in_(enrolled_course_ids)
        ).limit(4).all()
        
        if recommended:
            return jsonify([{
                'id': c.id,
                'title': c.title,
                'description': c.description[:100] + '...',
                'domain': c.domain,
                'level': c.level,
                'price': c.price,
                'instructor': c.instructor,
                'rating': c.rating,
                'students': c.students
            } for c in recommended])
    
    # Fallback to popular courses
    popular = Course.query.filter_by(status='approved').order_by(Course.students.desc()).limit(4).all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'description': c.description[:100] + '...',
        'domain': c.domain,
        'level': c.level,
        'price': c.price,
        'instructor': c.instructor,
        'rating': c.rating,
        'students': c.students
    } for c in popular])

# ==================== API ====================

@app.route('/api/courses/search')
def search_courses():
    query = request.args.get('q', '')
    domain = request.args.get('domain', 'all')
    level = request.args.get('level', 'all')
    price = request.args.get('price', 'all')
    
    courses_query = Course.query.filter_by(status='approved')
    
    if query:
        courses_query = courses_query.filter(
            Course.title.contains(query) | Course.description.contains(query)
        )
    if domain != 'all':
        courses_query = courses_query.filter_by(domain=domain)
    if level != 'all':
        courses_query = courses_query.filter_by(level=level)
    if price == 'free':
        courses_query = courses_query.filter_by(price=0)
    elif price == 'paid':
        courses_query = courses_query.filter(Course.price > 0)
    
    courses = courses_query.all()
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
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)