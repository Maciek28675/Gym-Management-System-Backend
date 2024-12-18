from flask import Blueprint, request, jsonify
from app import db
from sqlalchemy import text
from models import Customer, Subscription, Employee, Gym, GymClass
routes = Blueprint('routes', __name__)


@routes.route('/')
def home():
    try:
        result = db.session.execute(text('SELECT 1'))
        return "Database connection successful!", 200
    except Exception as e:
        return f"Error: {e}", 500