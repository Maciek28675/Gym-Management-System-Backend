from flask import Blueprint
from app import db
from sqlalchemy import text
routes = Blueprint('routes', __name__)


@routes.route('/')
def home():
    # return '<h1>Welcome to Gym Management 1.0</h1>'
    try:
        # Test the database connection with a simple query
        result = db.session.execute(text('SELECT 1'))
        return "Database connection successful!", 200
    except Exception as e:
        return f"Error: {e}", 500
