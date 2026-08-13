"""
Course Service - Business logic for course management
"""
from models import db, Course, Enrollment, Review
from sqlalchemy import func

def get_all_courses(status='approved'):
    """Get all courses with optional status filter"""
    return Course.query.filter_by(status=status).all()

def get_course_by_id(course_id):
    """Get a single course by ID"""
    return Course.query.get_or_404(course_id)

def create_course(data, instructor_id, instructor_name):
    """Create a new course"""
    course = Course(
        title=data.get('title'),
        description=data.get('description'),
        domain=data.get('domain'),
        level=data.get('level'),
        price=float(data.get('price', 0)),
        instructor=instructor_name,
        instructor_id=instructor_id,
        status='approved'
    )
    db.session.add(course)
    db.session.commit()
    return course

def update_course(course_id, data):
    """Update an existing course"""
    course = Course.query.get_or_404(course_id)
    course.title = data.get('title', course.title)
    course.description = data.get('description', course.description)
    course.domain = data.get('domain', course.domain)
    course.level = data.get('level', course.level)
    course.price = float(data.get('price', course.price))
    db.session.commit()
    return course

def delete_course(course_id):
    """Delete a course"""
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return True

def search_courses(query, domain, level, price):
    """Search courses with filters"""
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
    
    return courses_query.all()

def get_course_stats(course_id):
    """Get statistics for a course"""
    course = Course.query.get_or_404(course_id)
    enrollments = Enrollment.query.filter_by(course_id=course_id).count()
    reviews = Review.query.filter_by(course_id=course_id).all()
    
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    
    return {
        'enrollments': enrollments,
        'avg_rating': avg_rating,
        'total_reviews': len(reviews)
    }