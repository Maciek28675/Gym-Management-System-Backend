from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from .models import Employee


auth = Blueprint('auth', __name__)

@auth.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    employee_id = data['employee_id']
    password = data['password']
    gym_id = data['gym_id']
    first_name = data['first_name']
    last_name = data['last_name']
    role = data['role']

    user = Employee.query.filter_by(employee_id=employee_id).first()

    if user:
        return jsonify({"msg": "User already exists"}), 400

    hashed_password = Bcrypt.generate_password_hash(password).decode('utf-8')

    return jsonify({"msg": "User registered successfully"}), 201

@auth.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    employee_id = data['employee_id']
    password = data['password']

    print(f'Received data: {employee_id}; {password}')

    user = Employee.query.filter_by(employee_id=employee_id).first()

    print(f'user: {user}')
    
    if user and Bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.employee_id)

        return jsonify({'message': 'Login Success', 'access_token': access_token})
    else:
        return jsonify({'message': 'Login Failed'}), 401