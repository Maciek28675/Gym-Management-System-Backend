from flask import Blueprint, request, jsonify
from app.models import Subscription
from app import db
import logging

logging.basicConfig(level=logging.ERROR)

subscription_routes = Blueprint('subscription_routes', __name__)


@subscription_routes.route('/add_subscription', methods=['POST'])
def add_subscription():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'subscription_id', 'type', 'price', 'period'}
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['subscription_id'], int) or data['subscription_id'] <= 0:
        return jsonify({"msg": "subscription_id must be a positive integer"}), 400
    if not isinstance(data['price'], (float, int)) or data['price'] < 0:
        return jsonify({"msg": "price must be a positive number"}), 400
    if not isinstance(data['type'], str) or not data['type'].strip():
        return jsonify({"msg": "type must be a non-empty string"}), 400
    if not isinstance(data['period'], str) or not data['period'].strip():
        return jsonify({"msg": "period must be a non-empty string"}), 400

    try:
        subscription = Subscription.query.get(data['subscription_id'])
        if subscription:
            return jsonify({"msg": "Subscription already exists"}), 400

        new_subscription = Subscription(
            subscription_id=data['subscription_id'],
            type=data['type'],
            price=data['price'],
            period=data['period']
        )
        db.session.add(new_subscription)
        db.session.commit()
        return jsonify({"msg": "Subscription added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while adding subscription: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@subscription_routes.route('/update_subscription/<int:subscription_id>', methods=['PUT'])
def update_subscription(subscription_id):
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

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
        logging.error(f"An error occurred while updating subscription: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@subscription_routes.route('/delete_subscription/<int:subscription_id>', methods=['DELETE'])
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
        logging.error(f"An error occurred while deleting subscription: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@subscription_routes.route('/get_subscription/<int:subscription_id>', methods=['GET'])
def get_subscription(subscription_id):
    try:
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return jsonify({"msg": "Subscription does not exist"}), 404

        result = {
            "subscription_id": subscription.subscription_id,
            "type": subscription.type,
            "price": float(subscription.price),
            "period": subscription.period
        }
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving subscription: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
