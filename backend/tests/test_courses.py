import pytest
import sys
import os

# Add the backend directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    """Test client for the Flask application"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for tests
    with app.test_client() as client:
        with app.app_context():
            from models import db
            db.create_all()
            yield client
            db.drop_all()

def test_homepage(client):
    """Test that the homepage loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_courses_page(client):
    """Test that the courses page loads"""
    response = client.get('/courses')
    assert response.status_code == 200

def test_course_detail_404(client):
    """Test that a non-existent course returns 404"""
    response = client.get('/course/999')
    assert response.status_code == 404

def test_search_api(client):
    """Test the course search API"""
    response = client.get('/api/courses/search?q=python')
    assert response.status_code == 200
    assert response.is_json

def test_search_api_no_query(client):
    """Test search API with no query parameter"""
    response = client.get('/api/courses/search')
    assert response.status_code == 200
    assert response.is_json

def test_recommendations_api(client):
    """Test the recommendations API"""
    response = client.get('/api/courses/recommend')
    assert response.status_code == 200
    assert response.is_json

def test_signup_page(client):
    """Test that signup page loads"""
    response = client.get('/signup')
    assert response.status_code == 200

def test_login_page(client):
    """Test that login page loads"""
    response = client.get('/login')
    assert response.status_code == 200

def test_admin_courses_redirect_without_login(client):
    """Test that admin page redirects without login"""
    response = client.get('/admin/courses')
    assert response.status_code == 302  # Redirects to login