import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db

@pytest.fixture(scope='session')
def test_app():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

@pytest.fixture(scope='function')
def test_client(test_app):
    with test_app.test_client() as client:
        with test_app.app_context():
            db.create_all()
            yield client
            db.drop_all()