"""Flask application for Student Innovation Project webpage.

This module initializes the Flask application, configures extensions (Bootstrap,
SQLAlchemy, Bcrypt, LoginManager, Migrate), and registers the 'main' blueprint
for routes. The application uses Flask-Bootstrap for styling, Flask-SQLAlchemy
for database management, Flask-Bcrypt for password hashing, Flask-Login for
authentication, Flask-WTF for forms, python-markdown for rendering post content,
Flask-Migrate for database migrations, and SMTP2GO's API for contact form
submissions. It is designed for deployment on PythonAnywhere with code stored
on GitHub.
"""

import os

from dotenv import load_dotenv
from flask import Flask


from extensions import db, bcrypt, login_manager, migrate, bootstrap

# Load the environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Config Flask App
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# Configure database for production vs development
if os.environ.get('FLASK_ENV') == 'production':
    # Production MySQL configuration for PythonAnywhere
    mysql_username = 'ARolfeUAT'
    mysql_password = os.getenv('MYSQL_PASSWORD')
    mysql_host = 'ARolfeUAT.mysql.pythonanywhere-services.com'
    mysql_database = 'ARolfeUAT$default'  # Default database name format on PythonAnywhere

    app.config[
        'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_database}'
else:
    # Development SQLite configuration
    instance_path = os.path.abspath(os.path.join(app.root_path, 'instance'))
    os.makedirs(instance_path, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "sip.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SMTP2GO_API_KEY'] = os.getenv('SMTP2GO_API_KEY')
app.config['SMTP2GO_API_URL'] = os.getenv('SMTP2GO_API_URL')

# Initialize Flask Extensions
db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'main.login'
bootstrap.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login.

    Args:
        user_id: String, ID of the user to load.

    Returns:
        User: User object or None if not found.
    """
    from models import User

    return db.session.get(User, int(user_id))

from routes import main

app.register_blueprint(main)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
