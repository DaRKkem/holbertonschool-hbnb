import os

class Config:
    """Base configuration class."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

# DevelopmentConfig est utilisé par défaut dans create_app()
# via : app.config.from_object("config.developmentConfig")
