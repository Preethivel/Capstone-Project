"""
================================================================================
CAPSTONE PROJECT #80 - LearnVerse
Online Learning Platform with AI Features
MVP for Review 1 - 11 August 2026
================================================================================
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from models import db, User, Course, Enrollment
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learnverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ============================================================
# HOME PAGE
# ============================================================

@app.route('/')
def home():
    courses = Course.query.limit(6).all()
    trending = Course.query.order_by(Course.students.desc()).limit(4).all()
    
    avatar_categories = [
    {'name': 'Python', 'icon': '🐍', 'color': '#4B8BBE'},
    {'name': 'AI/ML', 'icon': '🤖', 'color': '#FF6B6B'},
    {'name': 'Web Dev', 'icon': '🌐', 'color': '#4ECDC4'},
    {'name': 'Data Science', 'icon': '📊', 'color': '#FFE66D'},
    {'name': 'Cloud', 'icon': '☁️', 'color': '#45B7D1'},
    {'name': 'DevOps', 'icon': '🚀', 'color': '#96CEB4'},
    {'name': 'Cybersecurity', 'icon': '🔒', 'color': '#FF6B6B'},
    {'name': 'Mobile Dev', 'icon': '📱', 'color': '#6C63FF'},
]
    return render_template('index.html', 
                         courses=courses, 
                         trending=trending,
                         avatar_categories=avatar_categories)

# ============================================================
# COURSES PAGE
# ============================================================

@app.route('/courses')
def courses():
    domain = request.args.get('domain', '')
    level = request.args.get('level', '')
    search = request.args.get('search', '')
    
    query = Course.query
    if domain:
        query = query.filter_by(domain=domain)
    if level:
        query = query.filter_by(level=level)
    if search:
        query = query.filter(Course.title.contains(search) | Course.description.contains(search))
    
    all_courses = query.all()
    domains = db.session.query(Course.domain).distinct().all()
    domains = [d[0] for d in domains]
    levels = ['Beginner', 'Intermediate', 'Advanced']
    
    return render_template('courses.html', courses=all_courses, domains=domains, levels=levels)

# ============================================================
# COURSE DETAIL
# ============================================================

@app.route('/course/<int:id>')
def course_detail(id):
    course = Course.query.get_or_404(id)
    return render_template('course_detail.html', course=course)

# ============================================================
# ADMIN - COURSE MANAGEMENT (CRUD)
# ============================================================

@app.route('/admin/courses')
def admin_courses():
    courses = Course.query.all()
    return render_template('admin_courses.html', courses=courses)

@app.route('/admin/course/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course = Course(
            title=request.form['title'],
            description=request.form['description'],
            domain=request.form['domain'],
            level=request.form['level'],
            price=float(request.form['price']),
            instructor=request.form['instructor']
        )
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('admin_courses'))
    return render_template('add_course.html')

@app.route('/admin/course/edit/<int:id>', methods=['GET', 'POST'])
def edit_course(id):
    course = Course.query.get_or_404(id)
    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form['description']
        course.domain = request.form['domain']
        course.level = request.form['level']
        course.price = float(request.form['price'])
        course.instructor = request.form['instructor']
        db.session.commit()
        return redirect(url_for('admin_courses'))
    return render_template('edit_course.html', course=course)

@app.route('/admin/course/delete/<int:id>')
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('admin_courses'))

# ============================================================
# RUN THE APP
# ============================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample courses if empty
        if Course.query.count() == 0:
            sample_courses = [
                ('Python Masterclass', 'Complete Python programming from zero to hero. Learn all concepts with hands-on projects.', 'Python', 'Beginner', 499, 'Dr. Sarah Johnson', 4.8, 12000),
                ('AI/ML Fundamentals', 'Learn Artificial Intelligence and Machine Learning from basics to advanced. Build real-world models.', 'AI/ML', 'Intermediate', 799, 'Prof. John Davis', 4.9, 8500),
                ('Full Stack Web Dev', 'Build complete web applications with React and Django. Master frontend and backend development.', 'Web Dev', 'Advanced', 999, 'Ms. Emily Wilson', 4.7, 6500),
                ('Data Science Bootcamp', 'Master data analysis, visualization, and machine learning with real-world datasets.', 'Data Science', 'Intermediate', 899, 'Dr. Michael Chen', 4.8, 7200),
                ('Cloud Computing with AWS', 'Deploy scalable applications on AWS cloud platform. Learn EC2, S3, Lambda and more.', 'Cloud', 'Intermediate', 699, 'Mr. David Kumar', 4.6, 5400),
                ('DevOps Engineering', 'Learn CI/CD, Docker, Kubernetes, and automation tools for modern software delivery.', 'DevOps', 'Advanced', 899, 'Ms. Lisa Park', 4.7, 4800),
                ('JavaScript Mastery', 'Master JavaScript from basics to advanced. Build interactive web applications.', 'Web Dev', 'Beginner', 399, 'Mr. James Smith', 4.5, 9800),
                ('Data Structures & Algorithms', 'Master DSA for coding interviews. Learn arrays, trees, graphs, and more.', 'Python', 'Intermediate', 599, 'Dr. Priya Patel', 4.6, 11000),
            ]
            for title, desc, domain, level, price, instructor, rating, students in sample_courses:
                db.session.add(Course(title=title, description=desc, domain=domain, level=level, price=price, instructor=instructor, rating=rating, students=students))
            db.session.commit()
            print("✅ Sample courses added!")
    
    print("\n🚀 LearnVerse is running!")
    print("📍 http://127.0.0.1:5000")
    app.run(debug=True)