from flask import Blueprint, request, jsonify
from app.models import Employee, GymClass
from app import db
import logging
from utils import role_required, check_gym_mismatch
from flask_jwt_extended import get_jwt

employee_routes = Blueprint('employee_routes', __name__)

ALLOWED_ROLES = ["manager", "receptionist", "coach"]


@employee_routes.route('/update_employee/<int:employee_id>', methods=['PUT'])
@role_required(["manager"])
def update_employee(employee_id):
    data = request.get_json()

    if not data:
        logging.error("No data provided for updating an employee")
        return jsonify({"msg": "No data provided"}), 400
    
    employee = Employee.query.get(employee_id)

    if not employee:
        logging.warning(f"Employee with ID {employee_id} does not exist")
        return jsonify({"msg": "Employee does not exist"}), 404

    allowed_fields = {'password', 'first_name', 'last_name', 'role'}
    
    # Check if the role is being changed from 'coach' to another role
    if 'role' in data and data['role'] != employee.role and employee.role == 'coach':
        try:
            gym_classes = GymClass.query.filter_by(employee_id=employee_id).all()
            for gym_class in gym_classes:
                gym_class.employee_id = None  # Remove the employee as the coach
            db.session.commit()
            logging.info(f"Employee {employee_id} removed from all gym classes they were coaching")
        except Exception as e:
            db.session.rollback()
            logging.error(f"An error occurred while removing employee {employee_id} from gym classes: {str(e)}")
            return jsonify({"msg": "An internal error occurred while updating gym classes"}), 500

    for key, value in data.items():
        if key not in allowed_fields:
            logging.error(f"Field '{key}' is not allowed for update")
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400

        if key == 'password' and len(value) < 8:
            logging.warning("Password length validation failed")
            return jsonify({"msg": "Password must be at least 8 characters long"}), 400

        if key == 'role' and value not in ALLOWED_ROLES:
            logging.error(f"Invalid role provided: {value}")
            return jsonify({"msg": f"Invalid role. Allowed roles are: {', '.join(ALLOWED_ROLES)}"}), 400

        setattr(employee, key, value)

    try:
        db.session.commit()
        logging.info(f"Employee updated successfully: ID {employee_id}")

        return jsonify({"msg": "Employee updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating an employee: {str(e)}")

        return jsonify({"msg": "An internal error occurred"}), 500


@employee_routes.route('/delete_employee/<int:employee_id>', methods=['DELETE'])
@role_required(["manager"])
def delete_employee(employee_id):

    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            logging.warning(f"Employee with ID {employee_id} does not exist")
            return jsonify({"msg": "Employee does not exist"}), 404
        
        jwt_payload = get_jwt()
        user_gym_id = jwt_payload.get('gym_id')

        if user_gym_id != employee.gym_id:
            logging.warning("You are not authorized to modify this gym")
            return jsonify({"msg": "You are not authorized to modify this gym"}), 403
        
        db.session.delete(employee)
        db.session.commit()
        logging.info(f"Employee deleted successfully: ID {employee_id}")
        return jsonify({"msg": "Employee deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while deleting an employee: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@employee_routes.route('/get_employee/<int:employee_id>', methods=['GET'])
@role_required(["manager"])
def get_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        logging.warning(f"Employee with ID {employee_id} does not exist")
        return jsonify({"msg": "Employee does not exist"}), 404
    
    result = {
        "employee_id": employee.employee_id,
        "gym_id": employee.gym_id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "role": employee.role,
    }
    logging.info(f"Employee retrieved successfully: ID {employee_id}")
    return jsonify(result), 200


@employee_routes.route('/get_all_employees', methods=['GET'])
@role_required(["manager"])
def get_all_employees():
    try:

        limit = request.args.get('limit', 5, type=int)
        offset = request.args.get('offset', 0, type=int)

        employees = Employee.query.order_by(Employee.employee_id).limit(limit).offset(offset).all()
        
        result = [
            {
                "employee_id": employee.employee_id,
                "gym_id": employee.gym_id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "role": employee.role,
            }
            for employee in employees
        ]
        logging.info("All employees retrieved successfully")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving all employees: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
