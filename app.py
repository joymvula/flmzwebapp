# flask_legacy_app/app.py
import click
from flask import Flask, redirect, url_for
from config import Config
from extensions import db, migrate, login
from werkzeug.security import generate_password_hash

# Application Factory
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # User loader for Flask-Login
    from models import User
    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import bp as auth_bp
    from routes.field_officer import bp as fo_bp
    from routes.teacher import bp as teacher_bp
    from routes.dashboard import bp as dash_bp
    from routes.api import bp as api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(fo_bp,   url_prefix='/fo')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(dash_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Root route
    @app.route('/')
    def root():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Expose RegistrationForm to all templates (for modals)
    @app.context_processor
    def inject_forms():
        from forms import RegistrationForm
        return dict(registration_form=RegistrationForm())
    

    @app.cli.command('init-db')
    def init_db():
        """Create all tables."""
        db.create_all()
        click.echo('✅ Initialized database.')

    @app.cli.command('create-admin')
    @click.argument('email')
    @click.argument('password')
    def create_admin(email, password):
        """Create an admin user with EMAIL and PASSWORD."""
        from models import User

        if User.query.filter_by(email=email).first():
            click.echo(f'⚠️  User {email} already exists.')
            return

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role='admin'
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f'🔑 Admin user {email} created.')

    return app

