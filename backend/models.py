from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='learner')
    organization = db.Column(db.String(200), nullable=True)
    title = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    badges = db.Column(db.JSON, default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Relationships - Using back_populates to avoid conflicts
    enrollments = db.relationship('Enrollment', back_populates='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', back_populates='user', lazy=True, cascade='all, delete-orphan')
    courses_created = db.relationship('Course', back_populates='creator', lazy=True)
    reviews = db.relationship('Review', back_populates='user', lazy=True, cascade='all, delete-orphan')

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, default=0.0)
    instructor = db.Column(db.String(100), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rating = db.Column(db.Float, default=0.0)
    students = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='approved')
    course_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Using back_populates
    enrollments = db.relationship('Enrollment', back_populates='course', lazy=True, cascade='all, delete-orphan')
    modules = db.relationship('Module', back_populates='course', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='course', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', back_populates='courses_created', foreign_keys=[instructor_id])

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)
    completed_lessons = db.Column(db.Integer, default=0)
    total_lessons = db.Column(db.Integer, default=0)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships - Using back_populates
    user = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', back_populates='modules')
    lessons = db.relationship('Lesson', back_populates='module', lazy=True, cascade='all, delete-orphan')

class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    content = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    module = db.relationship('Module', back_populates='lessons')
    completions = db.relationship('LessonCompletion', back_populates='lesson', lazy=True, cascade='all, delete-orphan')

class LessonCompletion(db.Model):
    __tablename__ = 'lesson_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='lesson_completions')
    lesson = db.relationship('Lesson', back_populates='completions')

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='payments')
    course = db.relationship('Course')

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='reviews')
    course = db.relationship('Course', back_populates='reviews')