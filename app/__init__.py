from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

from werkzeug.security import generate_password_hash

# Initialize Database and Login Manager
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize Plugins
    db.init_app(app)
    login_manager.init_app(app)

    # Create Uploads Folder if not exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Import and Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.home import home_bp
    # from app.routes.files import files_bp
    from app.routes.projects import projects_bp
    # from app.routes.share import share_bp
    from app.routes.admin import admin_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    # app.register_blueprint(files_bp, url_prefix='/files')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    # app.register_blueprint(share_bp, url_prefix='/share')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(profile_bp, url_prefix='/profile')

    return app


from app.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_admin_user():
    """Automatically creates an admin user if none exists."""
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✔ Admin user created automatically.")
    else:
        print("✔ Admin user already exists.")
