from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Course
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "learnverse.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_detail.html', course=course)

@app.route('/admin/courses')
def admin_courses():
    all_courses = Course.query.all()
    return render_template('admin_courses.html', courses=all_courses)

@app.route('/admin/course/add', methods=['GET', 'POST'])
def add_course():
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
        return redirect(url_for('admin_courses'))
    return render_template('add_course.html')

@app.route('/admin/course/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
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
        return redirect(url_for('admin_courses'))
    return render_template('edit_course.html', course=course)

@app.route('/admin/course/delete/<int:course_id>')
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('admin_courses'))

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