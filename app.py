from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from models import db, User, Course, Enrollment, Payment
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "learnverse.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ==================== ADMIN CHECK HELPER ====================

def is_admin():
    """Check if current user is admin"""
    return session.get('user_email') == 'admin@learnverse.com'

# ==================== AUTHENTICATION ====================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('signup'))
        
        user = User(name=name, email=email)
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
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user = User.query.get(user_id)
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    
    total_courses = len(enrollments)
    completed_courses = sum(1 for e in enrollments if e.progress == 100)
    total_xp = user.xp
    
    return render_template('dashboard.html', 
                         user=user, 
                         enrollments=enrollments,
                         total_courses=total_courses,
                         completed_courses=completed_courses,
                         total_xp=total_xp)

# ==================== COURSE ENROLLMENT ====================

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
        flash(f'You have been enrolled in "{course.title}"!', 'success')
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
        payment_method='Manual',
        completed_at=datetime.utcnow()
    )
    db.session.add(payment)
    
    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.session.add(enrollment)
    course.students += 1
    db.session.commit()
    
    flash(f'Payment successful! You are now enrolled in "{course.title}"', 'success')
    return redirect(url_for('dashboard'))

# ==================== EXISTING ROUTES ====================

@app.route('/')
def index():
    courses_count = Course.query.count()
    students_count = User.query.count()
    instructors_count = Course.query.with_entities(Course.instructor).distinct().count()
    
    return render_template('index.html', 
                         courses_count=courses_count,
                         students_count=students_count,
                         instructors_count=instructors_count)

@app.route('/courses')
def courses():
    all_courses = Course.query.all()
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

# ==================== ADMIN ROUTES ====================

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
            rating=float(request.form.get('rating', 0)),
            students=int(request.form.get('students', 0))
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
        course.rating = float(request.form.get('rating', 0))
        course.students = int(request.form.get('students', 0))
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

# ==================== API ROUTES ====================

@app.route('/api/courses/search')
def search_courses():
    query = request.args.get('q', '')
    domain = request.args.get('domain', 'all')
    level = request.args.get('level', 'all')
    price = request.args.get('price', 'all')
    
    courses_query = Course.query
    
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