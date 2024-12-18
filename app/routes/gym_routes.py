from flask import Blueprint, request, jsonify
from app import db
from sqlalchemy import text
from models import Customer, Subscription, Employee, Gym, GymClass

routes = Blueprint('gym', __name__)


@routes.route('/api/add_gym', methods=['POST'])
def add_gym():
    data = request.get_json()

    gym_id = data['gym_id']
    name = data['name']
    address = data['address']

    gym = Gym.query.filter_by(gym_id=gym_id).first()
    if gym:
        return jsonify({"msg": "Gym already exists"}), 400
    
    try:
        new_gym = Gym(
            gym_id=gym_id,
            name=name,
            address=address,
        )
        db.session.add(new_gym)
        db.session.commit()
        return jsonify({"msg": "Gym added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    

@routes.route('/api/get_gym/<int:gym_id>', methods=['GET'])
def get_gym(gym_id):
    gym = Gym.query.get(gym_id)
    if not gym:
        return jsonify({"msg": "Gym does not exist"}), 404

    result = {
        "gym_id": gym.gym_id,
        "name": gym.name,
        "address": gym.address,
    }
    return jsonify(result), 200