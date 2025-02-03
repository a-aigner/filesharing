import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    DATABASE_URL = os.getenv('DATABASE_URL')  # Allows easy switching

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL  # Use PostgreSQL if provided
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Default to SQLite

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
