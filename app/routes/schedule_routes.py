from flask import Blueprint, request, jsonify
from app.models import Schedule
from app import db
import logging

logging.basicConfig(level=logging.ERROR)

schedule_routes = Blueprint('schedule_routes', __name__)


@schedule_routes.route('/add_schedule', methods=['POST'])
def add_schedule():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'schedule_id', 'gymclass_id', 'gym_id', 'employee_id', 'day_otw', 'start_time', 'end_time'}
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['schedule_id'], int) or data['schedule_id'] <= 0:
        return jsonify({"msg": "schedule_id must be a positive integer"}), 400
    if not isinstance(data['gymclass_id'], int) or data['gymclass_id'] <= 0:
        return jsonify({"msg": "gymclass_id must be a positive integer"}), 400
    if not isinstance(data['gym_id'], int) or data['gym_id'] <= 0:
        return jsonify({"msg": "gym_id must be a positive integer"}), 400
    if not isinstance(data['employee_id'], int) or data['employee_id'] <= 0:
        return jsonify({"msg": "employee_id must be a positive integer"}), 400

    try:
        schedule = Schedule.query.get(data['schedule_id'])
        if schedule:
            return jsonify({"msg": "Schedule already exists"}), 400

        new_schedule = Schedule(
            schedule_id=data['schedule_id'],
            gymclass_id=data['gymclass_id'],
            gym_id=data['gym_id'],
            employee_id=data['employee_id'],
            day_otw=data['day_otw'],
            start_time=data['start_time'],
            end_time=data['end_time']
        )
        db.session.add(new_schedule)
        db.session.commit()
        return jsonify({"msg": "Schedule added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while adding schedule: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@schedule_routes.route('/update_schedule/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"msg": "Schedule does not exist"}), 404

    allowed_fields = {'gymclass_id', 'gym_id', 'employee_id', 'day_otw', 'start_time', 'end_time'}
    for key, value in data.items():
        if key not in allowed_fields:
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400
        setattr(schedule, key, value)

    try:
        db.session.commit()
        return jsonify({"msg": "Schedule updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating schedule: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@schedule_routes.route('/delete_schedule/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({"msg": "Schedule does not exist"}), 404

        db.session.delete(schedule)
        db.session.commit()
        return jsonify({"msg": "Schedule deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while deleting schedule: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@schedule_routes.route('/get_schedule/<int:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({"msg": "Schedule does not exist"}), 404

        result = {
            "schedule_id": schedule.schedule_id,
            "gymclass_id": schedule.gymclass_id,
            "gym_id": schedule.gym_id,
            "employee_id": schedule.employee_id,
            "day_otw": schedule.day_otw,
            "start_time": str(schedule.start_time),
            "end_time": str(schedule.end_time)
        }
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving schedule: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
