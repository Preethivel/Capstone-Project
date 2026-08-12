from flask import Blueprint, request, jsonify, session
from ..models import Course, Enrollment, User
from collections import Counter

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/courses/search')
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

@api_bp.route('/courses/recommend')
def recommend_courses():
    if 'user_id' not in session:
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
            'students': c.students,
            'reason': '🔥 Popular among students'
        } for c in popular])
    
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
                return jsonify([{
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
                } for c in recommended])
    
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
        'students': c.students,
        'reason': '🔥 Popular among students'
    } for c in popular])