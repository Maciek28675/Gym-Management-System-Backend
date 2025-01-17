from flask import Blueprint, request, jsonify
from app.models import Gym, Employee, Product, GymClass, Schedule
from app import db
import logging
from utils import role_required
from flask_jwt_extended import get_jwt

gym_routes = Blueprint('gym_routes', __name__)


@gym_routes.route('/add_gym', methods=['POST'])
@role_required(["manager"])
def add_gym():
    data = request.get_json()

    if not data:
        logging.error("No data provided for adding gym")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'name', 'address'}

    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['name'], str) or len(data['name']) < 2:
        logging.warning("Invalid name provided")
        return jsonify({"msg": "name must be a valid string with at least 2 characters"}), 400
    
    if not isinstance(data['address'], str) or len(data['address']) < 5:
        logging.warning("Invalid address provided")
        return jsonify({"msg": "address must be a valid string with at least 5 characters"}), 400

    try:
        new_gym = Gym(
            name=data['name'],
            address=data['address'],
        )

        db.session.add(new_gym)
        db.session.commit()

        logging.info(f"Gym added successfully")
        return jsonify({"msg": "Gym added successfully"}), 201
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while adding gym: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gym_routes.route('/update_gym/<int:gym_id>', methods=['PUT'])
@role_required(["manager"])
def update_gym(gym_id):
    data = request.get_json()

    if not data:
        logging.error("No data provided for updating gym")
        return jsonify({"msg": "No data provided"}), 400

    gym = Gym.query.get(gym_id)
    if not gym:
        logging.warning(f"Gym with ID {gym_id} does not exist")
        return jsonify({"msg": "Gym does not exist"}), 404

    jwt_payload = get_jwt()
    user_gym_id = jwt_payload.get('gym_id')

    if user_gym_id != data['gym_id']:
        logging.warning("You are not authorized to modify this gym")
        return jsonify({"msg": "You are not authorized to modify this gym"}), 403
    
    allowed_fields = {'name', 'address'}
    for key, value in data.items():
        if key not in allowed_fields:
            logging.error(f"Field '{key}' is not allowed for update")
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400
        setattr(gym, key, value)

    try:
        db.session.commit()
        logging.info(f"Gym {gym_id} updated successfully")
        return jsonify({"msg": "Gym updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating gym {gym_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gym_routes.route('/delete_gym/<int:gym_id>', methods=['DELETE'])
@role_required(["manager"])
def delete_gym(gym_id):
    try:
        gym = Gym.query.get(gym_id)
        if not gym:
            logging.warning(f"Gym with ID {gym_id} does not exist")
            return jsonify({"msg": "Gym does not exist"}), 404

        jwt_payload = get_jwt()
        user_gym_id = jwt_payload.get('gym_id')

        if user_gym_id != gym.gym_id:
            logging.warning("You are not authorized to modify this gym")
            return jsonify({"msg": "You are not authorized to modify this gym"}), 403
    
        Employee.query.filter_by(gym_id=gym_id).update({Employee.gym_id: None})
        Product.query.filter_by(gym_id=gym_id).update({Product.gym_id: None})
        GymClass.query.filter_by(gym_id=gym_id).update({GymClass.gym_id: None})
        Schedule.query.filter_by(gym_id=gym_id).update({Schedule.gym_id: None})

        db.session.delete(gym)
        db.session.commit()
        logging.info(f"Gym {gym_id} deleted successfully")
        return jsonify({"msg": "Gym deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while deleting gym {gym_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gym_routes.route('/get_gym/<int:gym_id>', methods=['GET'])
@role_required(["manager", "receptionist", "coach"])
def get_gym(gym_id):
    try:
        gym = Gym.query.get(gym_id)
        if not gym:
            logging.warning(f"Gym with ID {gym_id} does not exist")
            return jsonify({"msg": "Gym does not exist"}), 404

        result = {
            "gym_id": gym.gym_id,
            "name": gym.name,
            "address": gym.address,
        }
        logging.info(f"Gym retrieved successfully: ID {gym_id}")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving gym: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gym_routes.route('/get_all_gyms', methods=['GET'])
@role_required(["manager", "receptionist", "coach"])
def get_all_gyms():
    try:
        limit = request.args.get('limit', 5, type=int)
        offset = request.args.get('offset', 0, type=int)

        gyms = Gym.query.order_by(Gym.gym_id).limit(limit).offset(offset).all()
        result = [
            {
                "gym_id": gym.gym_id,
                "name": gym.name,
                "address": gym.address,
            } for gym in gyms
        ]
        logging.info("All gyms retrieved successfully")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving all gyms: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500