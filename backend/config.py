import os

class Config:
    SECRET_KEY = os.urandom(24)
    # Get the absolute path to the project root
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "database", "learnverse.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_EMAIL = 'admin@learnverse.com'