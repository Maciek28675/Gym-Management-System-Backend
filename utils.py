from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from functools import wraps
from app.models import Employee

def role_required(required_roles: list):
    def decorator(func):
        @jwt_required()
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            user_data = Employee.query.get(current_user)

            if user_data and user_data.role in required_roles:
                return func(*args, **kwargs)
            else:
                return jsonify({'msg': 'Access denied'}), 403
        return wrapper
    return decorator