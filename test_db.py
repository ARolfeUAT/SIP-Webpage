from app import create_app
from models import User

app = create_app()

with app.app_context():
    try:
        count = User.query.count()
        print(f"User count: {count}")
    except Exception as e:
        print(f"Error: {str(e)}")