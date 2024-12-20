from flask import Blueprint, request, jsonify
from app.models import Schedule
from app import db
import logging
from utils import role_required
schedule_routes = Blueprint('schedule_routes', __name__)


@schedule_routes.route('/add_schedule', methods=['POST'])
@role_required(["manager"])
def add_schedule():
    data = request.get_json()

    if not data:
        logging.error("No data provided for adding a schedule")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'gym_id', 'day_otw', 'start_time', 'end_time', 'entry_type'}

    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if 'employee_id' not in data and 'gymclass_id' not in data:
        logging.error("Either employee_id or gymclass_id must be provided")
        return jsonify({"msg": "Either employee_id or gymclass_id must be provided"}), 400
    
    if 'employee_id' in data and 'gymclass_id' in data:
        logging.error("Cannot enter both employee_id and gymclass_id as a schedule enetry")
        return jsonify({"msg": "Cannot enter both employee_id and gymclass_id as a schedule enetry"}), 400
    
    try:
        new_schedule = Schedule(
            gymclass_id=data.get('gymclass_id'),
            gym_id=data['gym_id'],
            employee_id=data.get('employee_id'),
            day_otw=data['day_otw'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            entry_type=data['entry_type']
        )

        db.session.add(new_schedule)
        db.session.commit()

        logging.info(f"Schedule added successfully")
        return jsonify({"msg": "Schedule added successfully"}), 201

    except Exception as e:
        db.session.rollback()

        logging.error(f"An error occurred while adding schedule: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@schedule_routes.route('/update_schedule/<int:schedule_id>', methods=['PUT'])
@role_required(["manager"])
def update_schedule(schedule_id):
    data = request.get_json()

    if not data:
        logging.error("No data provided for updating a schedule")
        return jsonify({"msg": "No data provided"}), 400

    schedule = Schedule.query.get(schedule_id)

    if not schedule:
        logging.error(f"Schedule with ID {schedule_id} does not exist")
        return jsonify({"msg": "Schedule does not exist"}), 404

    allowed_fields = {'gymclass_id', 'gym_id', 'employee_id', 'day_otw', 'start_time', 'end_time'}

    for key, value in data.items():
        if key not in allowed_fields:
            logging.error(f"Field '{key}' is not allowed for update")
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400
        
        setattr(schedule, key, value)

    try:
        db.session.commit()

        logging.info(f"Schedule {schedule_id} updated successfully")
        return jsonify({"msg": "Schedule updated successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        
        logging.error(f"An error occurred while updating schedule {schedule_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@schedule_routes.route('/delete_schedule/<int:schedule_id>', methods=['DELETE'])
@role_required(["manager"])
def delete_schedule(schedule_id):
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            logging.error(f"Schedule with ID {schedule_id} does not exist")
            return jsonify({"msg": "Schedule does not exist"}), 404

        db.session.delete(schedule)
        db.session.commit()
        logging.info(f"Schedule {schedule_id} deleted successfully")
        return jsonify({"msg": "Schedule deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while deleting schedule {schedule_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@schedule_routes.route('/get_schedule/<int:schedule_id>', methods=['GET'])
@role_required(["manager", "receptionist", "coach"])
def get_schedule(schedule_id):
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            logging.error(f"Schedule with ID {schedule_id} does not exist")
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
        logging.info(f"Schedule {schedule_id} retrieved successfully")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving schedule {schedule_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
    

@schedule_routes.route('/get_all_schedules', methods=['GET'])
@role_required(["manager", "receptionist", "coach"])
def get_all_schedules():
    try:
        schedules = Schedule.query.all()
        result = [
            {
                "schedule_id": schedule.schedule_id,
                "gymclass_id": schedule.gymclass_id,
                "gym_id": schedule.gym_id,
                "employee_id": schedule.employee_id,
                "day_otw": schedule.day_otw,
                "start_time": str(schedule.start_time),
                "end_time": str(schedule.end_time),
                "entry_type": schedule.entry_type,
            }
            for schedule in schedules
        ]
        logging.info("All schedules retrieved successfully")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving all schedules: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
