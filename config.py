import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your_secret_key_here"
    DEBUG = False
    TESTING = False

    # Database configuration
    DB_HOST = os.environ.get("DB_HOST") or "localhost"
    DB_USER = os.environ.get("DB_USER") or "root"
    DB_PASSWORD = os.environ.get("DB_PASSWORD") or "root123"
    DB_NAME = os.environ.get("DB_NAME") or "attendance_system"

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DB_NAME = "attendance_system_test"

class ProductionConfig(Config):
    """Production configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY")  # must be set in environment
    DEBUG = False
