from flask import Blueprint, request, jsonify
from app.models import Gym
from app import db
import logging

logging.basicConfig(level=logging.ERROR)

gym_routes = Blueprint('gym_routes', __name__)


@gym_routes.route('/add_gym', methods=['POST'])
def add_gym():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'gym_id', 'name', 'address'}
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['gym_id'], int) or data['gym_id'] <= 0:
        return jsonify({"msg": "gym_id must be a positive integer"}), 400
    if not isinstance(data['name'], str) or len(data['name']) < 2:
        return jsonify({"msg": "name must be a valid string with at least 2 characters"}), 400
    if not isinstance(data['address'], str) or len(data['address']) < 5:
        return jsonify({"msg": "address must be a valid string with at least 5 characters"}), 400

    gym = Gym.query.filter_by(gym_id=data['gym_id']).first()
    if gym:
        return jsonify({"msg": "Gym already exists"}), 400

    try:
        new_gym = Gym(
            gym_id=data['gym_id'],
            name=data['name'],
            address=data['address'],
        )
        db.session.add(new_gym)
        db.session.commit()
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
            return jsonify({"msg": "Gym does not exist"}), 404

        result = {
            "gym_id": gym.gym_id,
            "name": gym.name,
            "address": gym.address,
        }
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving gym: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
