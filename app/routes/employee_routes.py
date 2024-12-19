from flask import Blueprint, request, jsonify
from app.models import Employee
from app import db
import logging

logging.basicConfig(level=logging.ERROR)

employee_routes = Blueprint('employee_routes', __name__)


@employee_routes.route('/update_employee/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"msg": "Employee does not exist"}), 404

    allowed_fields = {'password', 'gym_id', 'first_name', 'last_name', 'role'}
    for key, value in data.items():
        if key not in allowed_fields:
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400

        if key == 'password' and len(value) < 8:
            return jsonify({"msg": "Password must be at least 8 characters long"}), 400

        setattr(employee, key, value)

    try:
        db.session.commit()
        return jsonify({"msg": "Employee updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@employee_routes.route('/delete_employee/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({"msg": "Employee does not exist"}), 404

        db.session.delete(employee)
        db.session.commit()
        return jsonify({"msg": "Employee deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@employee_routes.route('/get_employee/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"msg": "Employee does not exist"}), 404

    result = {
        "employee_id": employee.employee_id,
        "gym_id": employee.gym_id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "role": employee.role,
    }
    return jsonify(result), 200
