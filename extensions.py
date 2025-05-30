from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
bootstrap = Bootstrap5()
login_manager = LoginManager()
migrate = Migrate()
