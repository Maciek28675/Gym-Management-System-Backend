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


@auth.route('/first_register', methods=['POST'])
def first_register():
    manager_exists = Employee.query.filter_by(role='manager').first()

    if manager_exists:
        logging.error("Attempt to access 'first_register' route when a manager already exists.")
        return jsonify({'msg': "A manager already exists. This route is no longer accessible."}), 403
    
    data = request.get_json()

    if not data:
        logging.error("No data provided for 'first_register'")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'password', 'gym_id', 'first_name', 'last_name', 'role'}
    
    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field in 'first_register': {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if data['role'].lower() != 'manager':
        logging.error("Invalid role provided for 'first_register'. First user must be a manager.")
        return jsonify({"msg": "The first user must have the role 'manager'"}), 400


    try:
        bytes_password = data['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(bytes_password, salt).decode('utf-8')

        new_employee = Employee(
            password=hashed_password,
            gym_id=data['gym_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role']
        )

        db.session.add(new_employee)
        db.session.commit()
        logging.info(f"Manager registered successfully: {data['first_name']} {data['last_name']}, Gym ID: {data['gym_id']}")
        return jsonify({"msg": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred during registration: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
    

@auth.route('/register', methods=['POST'])
@role_required(['manager'])
def register():
    data = request.get_json()

    if not data:
        logging.error("No data provided for 'register'")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'password', 'gym_id', 'first_name', 'last_name', 'role'}

    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field in 'register': {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    try:
        bytes_password = data['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(bytes_password, salt).decode('utf-8')

        new_employee = Employee(
            password=hashed_password,
            gym_id=data['gym_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role']
        )

        db.session.add(new_employee)
        db.session.commit()
        logging.info(f"Employee registered successfully: {data['first_name']} {data['last_name']}, Role: {data['role']}, Gym ID: {data['gym_id']}")
        return jsonify({"msg": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred during registration: {str(e)}")

        return jsonify({"msg": "An internal error occurred"}), 500


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        logging.error("No data provided for login")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'employee_id', 'password', 'gym_id'}

    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    employee_id = data['employee_id']
    password = data['password']
    gym_id = data['gym_id']

    try:
        user = Employee.query.filter_by(employee_id=employee_id, gym_id=gym_id).first()
        if user:
            bytes_password = password.encode('utf-8')
            user_bytes = user.password.encode('utf-8')

            if bcrypt.checkpw(bytes_password, user_bytes):
                access_token = create_access_token(
                    identity=str(user.employee_id),
                    additional_claims={"role": user.role, "gym_id": gym_id}
                )
                logging.info(f"User {employee_id} logged in successfully at gym {gym_id}")
                return jsonify({'message': 'Login Success', 'access_token': access_token}), 200
            else:
                logging.warning(f"Failed login attempt for employee_id: {employee_id} at gym {gym_id}")
                return jsonify({'message': 'Invalid credentials'}), 401

        logging.warning(f"Login attempt for non-existing user or invalid gym: employee_id {employee_id}, gym_id {gym_id}")
        return jsonify({'message': 'User does not exist or gym mismatch'}), 404

    except Exception as e:
        logging.error(f"An error occurred during login: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
