from app import app, db
from models import Course, User
from datetime import datetime

def init_database():
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        # Sample courses
        sample_courses = [
            Course(
                title='Python for Beginners',
                description='Learn Python programming from scratch with hands-on projects',
                domain='Programming',
                level='Beginner',
                price=0,
                instructor='John Doe',
                rating=4.5,
                students=1200
            ),
            Course(
                title='Advanced Flask Development',
                description='Build scalable web applications with Flask and SQLAlchemy',
                domain='Web Development',
                level='Advanced',
                price=49.99,
                instructor='Jane Smith',
                rating=4.8,
                students=850
            ),
            Course(
                title='AI with Python',
                description='Introduction to Artificial Intelligence using Python libraries',
                domain='AI & ML',
                level='Intermediate',
                price=79.99,
                instructor='Dr. Alan Turing',
                rating=4.9,
                students=2100
            ),
            Course(
                title='Data Science Fundamentals',
                description='Learn data analysis, visualization, and statistics',
                domain='Data Science',
                level='Beginner',
                price=0,
                instructor='Marie Curie',
                rating=4.7,
                students=3500
            )
        ]
        
        for course in sample_courses:
            db.session.add(course)
        db.session.commit()
        print('✅ Database initialized with sample courses!')

if __name__ == '__main__':
    init_database()