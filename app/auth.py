from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token
import bcrypt
from .models import Employee
from . import db
from utils import role_required

auth = Blueprint('auth', __name__)


# TODO: dodać sprawdzanie poprawności danych
# TODO: dodać usuwanie konta admina przy rejestracji pierwszego managera

@auth.route('/api/register', methods=['POST'])
@role_required(['admin', 'manager'])
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

    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(bytes, salt).decode('utf-8')

    new_employee = Employee(
        employee_id=employee_id,
        password=hashed_password,
        gym_id=gym_id,
        first_name=first_name,
        last_name=last_name,
        role=role
    )

    db.session.add(new_employee)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201


@auth.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    employee_id = data['employee_id']
    password = data['password']

    print(f'Received data: {employee_id}; {password}')

    user = Employee.query.filter_by(employee_id=employee_id).first()

    if user:
        print(f'user: {user}')

        bytes = password.encode('utf-8')
        userBytes = user.password.encode('utf-8')

        if user and bcrypt.checkpw(bytes, userBytes):
            access_token = create_access_token(identity=user.employee_id, additional_claims={"role": user.role})

            return jsonify({'message': 'Login Success', 'access_token': access_token})
        else:
            return jsonify({'message': 'Login Failed'}), 401
    else:
        return jsonify({'message': 'user doesnt exist'}), 401