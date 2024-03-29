# Import necessary modules
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import generate_csrf
from flask_apscheduler import APScheduler
from flask_mail import Mail
from app.config import Config, MailConfig
from .utils import format_amount


# Create instances of Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

    # Load configuration from Config class
    app.config.from_object(Config)

    # Create uploads folder
    uploads_folder = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'profile')
    os.makedirs(uploads_folder, exist_ok=True)
    tmp_folder = os.path.join(app.root_path, 'frontend', 'static', 'uploads', 'tmp')
    os.makedirs(tmp_folder, exist_ok=True)


    with app.app_context():
        # Initialize the database with the Flask app
        db.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'

        # Import payment processor
        from app.backend.accounts.components.payment_processor import process_payments_with_context

        # Initialize the scheduler
        scheduler = APScheduler()
        scheduler.init_app(app)

        # Add job to schedule the payment processing function
        scheduler.add_job(id='process_payments', func=process_payments_with_context, trigger='interval', hours=6)

        # Start the scheduler
        scheduler.start()

        # Import blueprints
        from .backend.landing.routes import landing_bp
        from .backend.auth.routes import auth_bp
        from .backend.accounts import accounts_bp
        from .backend.accounts.components.accounts_context import accounts_context, inject_now

        # Register blueprints
        app.register_blueprint(landing_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(accounts_bp)

        # Query mail settings from the database
        from .backend.database.models import MailSettings

        mail_settings = MailSettings.query.first()
        if mail_settings:
            app.config['MAIL_SERVER'] = f'smtp.{mail_settings.mail_server}.com'
            app.config['MAIL_PORT'] = 465
            app.config['MAIL_USERNAME'] = mail_settings.company_email
            app.config['MAIL_PASSWORD'] = mail_settings.password
            app.config['MAIL_USE_TLS'] = False
            app.config['MAIL_USE_SSL'] = True
        else:
            app.config.from_object(MailConfig)

        # Initialize the mail
        mail.init_app(app)

        # Register the context processor
        app.context_processor(accounts_context)
        app.context_processor(inject_now)

        # Flask-Login user loader
        from .backend.database.models import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Generate CSRF token and make it available in the template context
        app.jinja_env.globals['csrf_token'] = generate_csrf

        # Register the filter with Jinja2
        app.jinja_env.filters['format_amount'] = format_amount

    return app
