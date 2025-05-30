import sys
import os

# Add your project directory to the Python path
project_home = '/home/ARolfeUAT/SIP-Webpage'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables if needed
os.environ['FLASK_ENV'] = 'production'

from app import app as application

if __name__ == "__main__":
    application.run()