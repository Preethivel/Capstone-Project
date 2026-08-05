from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    badges = db.Column(db.Text, default='[]')  # JSON array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, default=0)
    instructor = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, default=0)
    students = db.Column(db.Integer, default=0)
    image = db.Column(db.String(200), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    progress = db.Column(db.Integer, default=0)  # percentage
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)