from flask import Blueprint, request, jsonify
from app.models import GymClass, Employee, Gym, Customer, CustomerGymClass
from app import db
import logging
from datetime import datetime

gymclass_routes = Blueprint('gymclass_routes', __name__)


@gymclass_routes.route('/add_gymclass', methods=['POST'])
def add_gymclass():
    data = request.get_json()

    if not data:
        logging.error("No data provided for adding gym class")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'employee_id', 'gym_id', 'name', 'max_people', 'time', 'day_otw', 'signed_people'}

    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400
    
    try:
        is_time_valid = datetime.strptime(data['time'], "%H:%M:%S")
    except ValueError:
        logging.error("Time has to be in format HH:MM:SS")
        return jsonify({"msg": "Wrong time format (HH:MM:SS expected)"}), 400
    
    try:
        employee = Employee.query.get(data['employee_id'])

        if not employee:
            logging.warning(f"Employee with ID {data['employee_id']} does not exist")
            return jsonify({"msg": "Employee does not exist"}), 404

        gym = Gym.query.get(data['gym_id'])

        if not gym:
            logging.warning(f"Gym with ID {data['gym_id']} does not exist")
            return jsonify({"msg": "Gym does not exist"}), 404

        new_gymclass = GymClass(
            employee_id=data['employee_id'],
            gym_id=data['gym_id'],
            name=data['name'],
            max_people=data['max_people'],
            time=data['time'],
            day_otw=data['day_otw'],
            signed_people=data['signed_people']
        )

        db.session.add(new_gymclass)
        db.session.commit()

        logging.info(f"Gym class added successfully")
        return jsonify({"msg": "Gym class added successfully"}), 201

    except Exception as e:
        db.session.rollback()

        logging.error(f"An error occurred while adding gym class: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gymclass_routes.route('/update_gymclass/<int:gymclass_id>', methods=['PUT'])
def update_gymclass(gymclass_id):
    data = request.get_json()

    if not data:
        logging.error("No data provided for updating gym class")
        return jsonify({"msg": "No data provided"}), 400

    gymclass = GymClass.query.get(gymclass_id)
    if not gymclass:
        logging.warning(f"Gym class with ID {gymclass_id} does not exist")
        return jsonify({"msg": "Gym class does not exist"}), 404

    allowed_fields = {'employee_id', 'gym_id', 'name', 'max_people', 'time', 'day_otw', 'signed_people'}
    for key, value in data.items():
        if key not in allowed_fields:
            logging.warning(f"Field '{key}' is not allowed for update")
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400

        setattr(gymclass, key, value)

    try:
        db.session.commit()
        logging.info(f"Gym class updated successfully: ID {gymclass_id}")
        return jsonify({"msg": "Gym class updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating gym class: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gymclass_routes.route('/delete_gymclass/<int:gymclass_id>', methods=['DELETE'])
def delete_gymclass(gymclass_id):
    try:
        gymclass = GymClass.query.get(gymclass_id)
        if not gymclass:
            logging.warning(f"Gym class with ID {gymclass_id} does not exist")
            return jsonify({"msg": "Gym class does not exist"}), 404

        db.session.delete(gymclass)
        db.session.commit()
        logging.info(f"Gym class deleted successfully: ID {gymclass_id}")
        return jsonify({"msg": "Gym class deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while deleting gym class: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gymclass_routes.route('/get_gymclass/<int:gymclass_id>', methods=['GET'])
def get_gymclass(gymclass_id):
    try:
        gymclass = GymClass.query.get(gymclass_id)
        if not gymclass:
            logging.warning(f"Gym class with ID {gymclass_id} does not exist")
            return jsonify({"msg": "Gym class does not exist"}), 404

        result = {
            "gymclass_id": gymclass.gymclass_id,
            "employee_id": gymclass.employee_id,
            "gym_id": gymclass.gym_id,
            "name": gymclass.name,
            "max_people": gymclass.max_people,
            "time": str(gymclass.time),
            "day_otw": gymclass.day_otw,
            "signed_people": gymclass.signed_people,
        }
        logging.info(f"Gym class retrieved successfully: ID {gymclass_id}")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving gym class: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gymclass_routes.route('/enroll_customer/<int:gymclass_id>', methods=['POST'])
def enroll_customer(gymclass_id):
    data = request.get_json()

    if 'customer_id' not in data:
        logging.warning("Customer ID is required for enrollment")
        return jsonify({"msg": "Customer ID is required"}), 400

    customer_id = data['customer_id']

    customer = Customer.query.get(customer_id)

    if not customer:
        logging.warning(f"Customer with ID {customer_id} does not exist")
        return jsonify({"msg": "Customer does not exist"}), 404

    gym_class = GymClass.query.get(gymclass_id)

    if not gym_class:
        logging.warning(f"Gym class with ID {gymclass_id} does not exist")
        return jsonify({"msg": "Gym class does not exist"}), 404

    if gym_class.signed_people >= gym_class.max_people:
        logging.warning(f"Gym class ID {gymclass_id} is full")
        return jsonify({"msg": "No available spots in this class"}), 400

    existing_enrollment = CustomerGymClass.query.filter_by(customer_id=customer_id, gymclass_id=gymclass_id).first()
    
    if existing_enrollment:
        logging.warning(f"Customer ID {customer_id} is already enrolled in gym class ID {gymclass_id}")
        return jsonify({"msg": "Customer already enrolled in this class"}), 400

    try:
        new_enrollment = CustomerGymClass(customer_id=customer_id, gymclass_id=gymclass_id)
        gym_class.signed_people += 1
        db.session.add(new_enrollment)
        db.session.commit()
        logging.info(f"Customer ID {customer_id} enrolled successfully in gym class ID {gymclass_id}")
        return jsonify({"msg": "Customer enrolled successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred during enrollment: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gymclass_routes.route('/unenroll_customer/<int:gymclass_id>', methods=['POST'])
def unenroll_customer(gymclass_id):
    data = request.get_json()

    if 'customer_id' not in data:
        logging.warning("Customer ID is required for unenrollment")
        return jsonify({"msg": "Customer ID is required"}), 400

    customer_id = data['customer_id']

    enrollment = CustomerGymClass.query.filter_by(customer_id=customer_id, gymclass_id=gymclass_id).first()
    if not enrollment:
        logging.warning(f"Customer ID {customer_id} is not enrolled in gym class ID {gymclass_id}")
        return jsonify({"msg": "Customer is not enrolled in this class"}), 404

    try:
        gym_class = GymClass.query.get(gymclass_id)
        gym_class.signed_people -= 1
        db.session.delete(enrollment)
        db.session.commit()
        logging.info(f"Customer ID {customer_id} unenrolled successfully from gym class ID {gymclass_id}")
        return jsonify({"msg": "Customer unenrolled successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred during unenrollment: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
