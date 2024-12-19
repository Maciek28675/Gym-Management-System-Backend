from flask import Blueprint, request, jsonify
from app.models import GymClass, Employee, Gym, CustomerGymClass
from app import db
import logging

logging.basicConfig(level=logging.ERROR)

gymclass_routes = Blueprint('gymclass_routes', __name__)


@gymclass_routes.route('/add_gymclass', methods=['POST'])
def add_gymclass():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'gymclass_id', 'employee_id', 'gym_id', 'name', 'max_people', 'time', 'day_otw', 'signed_people'}
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['gymclass_id'], int) or data['gymclass_id'] <= 0:
        return jsonify({"msg": "gymclass_id must be a positive integer"}), 400
    if not isinstance(data['employee_id'], int) or data['employee_id'] <= 0:
        return jsonify({"msg": "employee_id must be a positive integer"}), 400
    if not isinstance(data['gym_id'], int) or data['gym_id'] <= 0:
        return jsonify({"msg": "gym_id must be a positive integer"}), 400
    if not isinstance(data['max_people'], int) or data['max_people'] <= 0:
        return jsonify({"msg": "max_people must be a positive integer"}), 400

    try:
        employee = Employee.query.get(data['employee_id'])
        if not employee:
            return jsonify({"msg": "Employee does not exist"}), 404

        gym = Gym.query.get(data['gym_id'])
        if not gym:
            return jsonify({"msg": "Gym does not exist"}), 404

        new_gymclass = GymClass(
            gymclass_id=data['gymclass_id'],
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
        return jsonify({"msg": "Gym class added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while adding gymclass: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gymclass_routes.route('/update_gymclass/<int:gymclass_id>', methods=['PUT'])
def update_gymclass(gymclass_id):
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    gymclass = GymClass.query.get(gymclass_id)
    if not gymclass:
        return jsonify({"msg": "Gym class does not exist"}), 404

    allowed_fields = {'employee_id', 'gym_id', 'name', 'max_people', 'time', 'day_otw', 'signed_people'}
    for key, value in data.items():
        if key not in allowed_fields:
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400

        setattr(gymclass, key, value)

    try:
        db.session.commit()
        return jsonify({"msg": "Gym class updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating gymclass: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gymclass_routes.route('/delete_gymclass/<int:gymclass_id>', methods=['DELETE'])
def delete_gymclass(gymclass_id):
    try:
        gymclass = GymClass.query.get(gymclass_id)
        if not gymclass:
            return jsonify({"msg": "Gym class does not exist"}), 404

        db.session.delete(gymclass)
        db.session.commit()
        return jsonify({"msg": "Gym class deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while deleting gymclass: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gymclass_routes.route('/get_gymclass/<int:gymclass_id>', methods=['GET'])
def get_gymclass(gymclass_id):
    try:
        gymclass = GymClass.query.get(gymclass_id)
        if not gymclass:
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
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving gymclass: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
    
from app.models import Customer, GymClass, CustomerGymClass
from app import db
from flask import Blueprint, request, jsonify
import logging

gymclass_routes = Blueprint('gymclass_routes', __name__)

logging.basicConfig(level=logging.ERROR)


@gymclass_routes.route('/enroll_customer/<int:gymclass_id>', methods=['POST'])
def enroll_customer(gymclass_id):
    data = request.get_json()

    if 'customer_id' not in data:
        return jsonify({"msg": "Customer ID is required"}), 400

    customer_id = data['customer_id']

    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"msg": "Customer does not exist"}), 404

    gym_class = GymClass.query.get(gymclass_id)
    if not gym_class:
        return jsonify({"msg": "Gym class does not exist"}), 404

    if gym_class.signed_people >= gym_class.max_people:
        return jsonify({"msg": "No available spots in this class"}), 400

    existing_enrollment = CustomerGymClass.query.filter_by(customer_id=customer_id, gymclass_id=gymclass_id).first()
    if existing_enrollment:
        return jsonify({"msg": "Customer already enrolled in this class"}), 400

    try:
        new_enrollment = CustomerGymClass(customer_id=customer_id, gymclass_id=gymclass_id)
        gym_class.signed_people += 1
        db.session.add(new_enrollment)
        db.session.commit()
        return jsonify({"msg": "Customer enrolled successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500

@gymclass_routes.route('/unenroll_customer/<int:gymclass_id>', methods=['POST'])
def unenroll_customer(gymclass_id):
    data = request.get_json()

    if 'customer_id' not in data:
        return jsonify({"msg": "Customer ID is required"}), 400

    customer_id = data['customer_id']

    enrollment = CustomerGymClass.query.filter_by(customer_id=customer_id, gymclass_id=gymclass_id).first()
    if not enrollment:
        return jsonify({"msg": "Customer is not enrolled in this class"}), 404

    try:
        gym_class = GymClass.query.get(gymclass_id)
        gym_class.signed_people -= 1
        db.session.delete(enrollment)
        db.session.commit()
        return jsonify({"msg": "Customer unenrolled successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
