from flask import Blueprint, request, jsonify
from app.models import Gym
from app import db
import logging

gym_routes = Blueprint('gym_routes', __name__)


@gym_routes.route('/add_gym', methods=['POST'])
def add_gym():
    data = request.get_json()

    if not data:
        logging.error("No data provided for adding gym")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'gym_id', 'name', 'address'}
    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['gym_id'], int) or data['gym_id'] <= 0:
        logging.warning("Invalid gym_id provided")
        return jsonify({"msg": "gym_id must be a positive integer"}), 400
    if not isinstance(data['name'], str) or len(data['name']) < 2:
        logging.warning("Invalid name provided")
        return jsonify({"msg": "name must be a valid string with at least 2 characters"}), 400
    if not isinstance(data['address'], str) or len(data['address']) < 5:
        logging.warning("Invalid address provided")
        return jsonify({"msg": "address must be a valid string with at least 5 characters"}), 400

    gym = Gym.query.filter_by(gym_id=data['gym_id']).first()
    if gym:
        logging.warning(f"Gym with ID {data['gym_id']} already exists")
        return jsonify({"msg": "Gym already exists"}), 400

    try:
        new_gym = Gym(
            gym_id=data['gym_id'],
            name=data['name'],
            address=data['address'],
        )
        db.session.add(new_gym)
        db.session.commit()
        logging.info(f"Gym added successfully: ID {data['gym_id']}")
        return jsonify({"msg": "Gym added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while adding gym: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@gym_routes.route('/get_gym/<int:gym_id>', methods=['GET'])
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
