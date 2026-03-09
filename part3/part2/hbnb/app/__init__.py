"""
Application factory module.

Creates and configures the Flask application instance
for the HBnB project.
"""

from flask import Flask
from app.api import api_bp


def create_app(config_class="config.DevelopmentConfig"):
    """
    Application factory function.

    Args:
        config_class (str): Dotted path to the configuration class.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    app.config.from_object(config_class)

    from app.services import facade
    facade.reset()

    # Register API Blueprint
    app.register_blueprint(api_bp)

    return app
