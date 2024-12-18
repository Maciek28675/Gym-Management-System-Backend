from flask import Blueprint, request, jsonify
from app import db
from sqlalchemy import text
from models import Customer, Subscription, Employee, Gym, GymClass

routes = Blueprint('gymclass', __name__)


@routes.route('/api/add_subscription', methods=['POST'])
def add_subscription():
    data = request.get_json()

    subscription_id = data['subscription_id']
    type = data['type']
    price = data['price']
    period = data['period']

    subscription = Subscription.query.filter_by(subscription_id=subscription_id).first()
    if subscription:
        return jsonify({"msg": "Subscription already exists"}), 400
    
    try:
        new_subscription = Subscription(
            subscription_id=subscription_id,
            type=type,
            price=price,
            period=period,
        )
        db.session.add(new_subscription)
        db.session.commit()
        return jsonify({"msg": "Subscription added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    

@routes.route('/api/update_subscription/<int:subscription_id>', methods=['PUT'])
def update_subscription(subscription_id):
    data = request.get_json()

    subscription = Subscription.query.get(subscription_id)
    if not subscription:
        return jsonify({"msg": "Subscription does not exist"}), 404

    allowed_fields = {'type', 'price', 'period'}

    for key, value in data.items():
        if key not in allowed_fields:
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400
        setattr(subscription, key, value)

    try:
        db.session.commit()
        return jsonify({"msg": "Subscription updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    

@routes.route('/api/delete_subscription/<int:subscription_id>', methods=['DELETE'])
def delete_subscription(subscription_id):
    try:
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return jsonify({"msg": "Subscription does not exist"}), 404

        db.session.delete(subscription)
        db.session.commit()
        return jsonify({"msg": "Subscription deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    

@routes.route('/api/get_subscription/<int:subscription_id>', methods=['GET'])
def get_subscription(subscription_id):
    subscription = Subscription.query.get(subscription_id)
    if not subscription:
        return jsonify({"msg": "Subscription does not exist"}), 404

    result = {
        "subscription_id": subscription.subscription_id,
        "type": subscription.type,
        "price": subscription.price,
        "period": subscription.period,
    }
    return jsonify(result), 200