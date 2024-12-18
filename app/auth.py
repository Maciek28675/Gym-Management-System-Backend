from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token
import bcrypt
import logging
from .models import Employee
from . import db
from utils import role_required

logging.basicConfig(level=logging.ERROR)

auth = Blueprint('auth', __name__)

@auth.route('/api/register', methods=['POST'])
@role_required(['admin', 'manager'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'employee_id', 'password', 'gym_id', 'first_name', 'last_name', 'role'}
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if data['employee_id'] == 1 and data['role'].lower() != 'manager':
        return jsonify({"msg": "The first user (employee_id=1) must have the role 'manager'"}), 400

    user = Employee.query.filter_by(employee_id=data['employee_id']).first()
    if user:
        return jsonify({"msg": "User already exists"}), 400

    try:
        bytes_password = data['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(bytes_password, salt).decode('utf-8')

        new_employee = Employee(
            employee_id=data['employee_id'],
            password=hashed_password,
            gym_id=data['gym_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role']
        )

        db.session.add(new_employee)
        db.session.commit()
        return jsonify({"msg": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred during registration: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@auth.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'employee_id', 'password'}
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    employee_id = data['employee_id']
    password = data['password']

    try:
        user = Employee.query.filter_by(employee_id=employee_id).first()
        if user:
            bytes_password = password.encode('utf-8')
            user_bytes = user.password.encode('utf-8')

            if bcrypt.checkpw(bytes_password, user_bytes):
                access_token = create_access_token(identity=user.employee_id, additional_claims={"role": user.role})
                return jsonify({'message': 'Login Success', 'access_token': access_token}), 200
            else:
                logging.warning(f"Failed login attempt for employee_id: {employee_id}")
                return jsonify({'message': 'Invalid credentials'}), 401

        logging.warning(f"Login attempt for non-existing user: {employee_id}")
        return jsonify({'message': 'User does not exist'}), 404

    except Exception as e:
        logging.error(f"An error occurred during login: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
