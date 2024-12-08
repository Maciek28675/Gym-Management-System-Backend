from flask import Blueprint
from app import db
from sqlalchemy import text
routes = Blueprint('routes', __name__)


@routes.route('/')
def home():
    try:
        result = db.session.execute(text('SELECT 1'))
        return "Database connection successful!", 200
    except Exception as e:
        return f"Error: {e}", 500
