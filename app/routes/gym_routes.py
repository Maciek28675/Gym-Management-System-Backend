from flask import Blueprint, request, jsonify
from app.models import Gym
from app import db
import logging
from utils import role_required

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
