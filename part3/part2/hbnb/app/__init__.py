"""
Application factory module.

Creates and configures the Flask application instance
for the HBnB project.
"""

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

bcrypt = Bcrypt()
jwt = JWTManager()

from app.api import api_bp


def create_app(config_class="config.DevelopmentConfig"):
    """
    Application factory function.

    Args:
        config_class (str): Dotted path to the configuration class.
                            Defaults to DevelopmentConfig.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    app.config.from_object(config_class)

    bcrypt.init_app(app)
    jwt.init_app(app)

    from app.services import facade
    facade.reset()

    # Register API Blueprint
    app.register_blueprint(api_bp)

    return app
