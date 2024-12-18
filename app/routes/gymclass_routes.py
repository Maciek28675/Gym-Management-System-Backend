from flask import Blueprint, request, jsonify
from app import db
from sqlalchemy import text
from models import Customer, Subscription, Employee, Gym, GymClass

routes = Blueprint('gymclass', __name__)


@routes.route('/api/add_gymclass', methods=['POST'])
def add_gymclass():
    data = request.get_json()

    gymclass_id = data['gymclass_id']
    employee_id = data['employee_id']
    gym_id = data['gym_id']
    name = data['name']
    max_people = data['max_people']
    time = data['time']
    day_otw = data['day_otw']
    signed_people = data['signed_people']
    
    try:
        employee = Employee.query.filter_by(employee_id=data['employee_id']).first()
        if not employee:
            return jsonify({"msg": "Employee does not exist"}), 404
        
        gym = Gym.query.filter_by(gym_id=data['gym_id']).first()
        if not gym:
            return jsonify({"msg": "Gym does not exist"}), 404
        
        new_gymclass = GymClass(
            gymclass_id=gymclass_id,
            employee_id=employee_id,
            gym_id=gym_id,
            name=name,
            max_people=max_people,
            time=time,
            day_otw=day_otw,
            signed_people=signed_people
        )
        db.session.add(new_gymclass)
        db.session.commit()
        return jsonify({"msg": "Gym class added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    

@routes.route('/api/update_gymclass/<int:gymclass_id>', methods=['PUT'])
def update_gymclass(gymclass_id):
    data = request.get_json()

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
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    

@routes.route('/api/delete_gymclass/<int:gymclass_id>', methods=['DELETE'])
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
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    

@routes.route('/api/get_gymclass/<int:gymclass_id>', methods=['GET'])
def get_gymclass(gymclass_id):
    gymclass = GymClass.query.get(gymclass_id)
    if not gymclass:
        return jsonify({"msg": "Gym class does not exist"}), 404

    result = {
        "gymclass_id": gymclass.gymclass_id,
        "employee_id": gymclass.employee_id,
        "gym_id": gymclass.gym_id,
        "name": gymclass.name,
        "max_people": gymclass.max_people,
        "time": gymclass.time,
        "day_otw": gymclass.day_otw,
        "signed_people": gymclass.signed_people,
    }
    return jsonify(result), 200