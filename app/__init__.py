"""
Scooter Share Pro - Flask Application Factory
Enterprise E-Scooter Rental Platform
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_restx import Api
from flask_cors import CORS
from datetime import datetime
import pytz

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
login_manager = LoginManager()
mail = Mail()
cors = CORS()

# Define timezone
timezone = pytz.timezone('Europe/Zurich')

def create_app(config_name='development'):
    """Application factory pattern"""
    from config import config as config_dict
    
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    api.init_app(app)
    
    # Add template filter for local time
    @app.template_filter('localtime')
    def localtime_filter(dt):
        """Convert UTC datetime to local timezone"""
        if dt is None:
            return None
        # Convert UTC to local timezone
        utc_dt = dt.replace(tzinfo=pytz.UTC)
        local_dt = utc_dt.astimezone(timezone)
        return local_dt
    
    # Configure login manager
    login_manager.login_view = 'web.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.web import bp as web_bp
    app.register_blueprint(web_bp)
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register API namespaces first
    from app.api import auth_ns, scooters_ns, rentals_ns, users_ns
    
    # API documentation
    api = Api(
        app,
        version='1.0',
        title='Scooter Share Pro API',
        description='Enterprise E-Scooter Rental Platform API',
        doc='/api/docs/'
    )
    
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(scooters_ns, path='/scooters')
    api.add_namespace(rentals_ns, path='/rentals')
    api.add_namespace(users_ns, path='/users')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Forbidden'}, 403
    
    # Initialize database tables immediately after app creation
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            # Ignore duplicate ENUM type errors (happens on redeploy)
            if "duplicate key value violates unique constraint" not in str(e):
                app.logger.error(f"Database initialization error: {e}")
    
    return app
