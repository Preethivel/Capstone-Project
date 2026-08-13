"""
API Routes - REST endpoints for frontend consumption

This module handles all API endpoints for course search,
recommendations, and other AJAX functionality.
"""

from flask import Blueprint, request, session, jsonify
from models import Course, Enrollment
from services.course_service import search_courses
from collections import Counter

api_bp = Blueprint('api', __name__, url_prefix='/api')


def api_response(success=True, message="", data=None, status_code=200):
    """
    Standard API response format for all endpoints.
    
    Args:
        success (bool): Whether the request was successful
        message (str): Response message
        data: Response data (any type)
        status_code (int): HTTP status code
        
    Returns:
        tuple: (json_response, status_code)
    """
    response = {
        'success': success,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code


@api_bp.route('/courses/search')
def search():
    """
    Search for courses with filters.
    
    Query Parameters:
        q: Search query (title or description)
        domain: Filter by domain
        level: Filter by level
        price: Filter by price (free/paid)
    
    Returns:
        JSON with matching courses
    """
    query = request.args.get('q', '')
    domain = request.args.get('domain', 'all')
    level = request.args.get('level', 'all')
    price = request.args.get('price', 'all')
    
    courses = search_courses(query, domain, level, price)
    
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


@api_bp.route('/courses/recommend')
def recommend():
    """
    AI-based course recommendations using content-based filtering.
    
    Returns:
        JSON with personalized course recommendations based on user's enrolled courses.
        Falls back to popular courses if user has no enrollments.
    """
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