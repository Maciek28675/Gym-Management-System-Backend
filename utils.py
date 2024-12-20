from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import jsonify
from functools import wraps
from app.models import Employee
import logging

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


def check_gym_mismatch(data):
    jwt_payload = get_jwt()
    user_gym_id = jwt_payload.get('gym_id')

    if user_gym_id != data['gym_id']:
        logging.warning("You are not authorized to modify this gym")
        return jsonify({"msg": "You are not authorized to modify this gym"}), 403