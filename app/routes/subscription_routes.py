from flask import Blueprint, request, jsonify
from app.models import Subscription, Customer
from app import db
import logging
from utils import role_required
subscription_routes = Blueprint('subscription_routes', __name__)


@subscription_routes.route('/add_subscription', methods=['POST'])
@role_required(["manager"])
def add_subscription():
    data = request.get_json()

    if not data:
        logging.error("No data provided for adding a subscription")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'type', 'price', 'period'}

    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['price'], (float, int)) or data['price'] < 0:
        logging.error("Invalid price value")
        return jsonify({"msg": "price must be a positive number"}), 400
    
    if not isinstance(data['type'], str) or not data['type'].strip():
        logging.error("Invalid type value")
        return jsonify({"msg": "type must be a non-empty string"}), 400
    
    if not isinstance(data['period'], int) or data['period'] < 0:
        logging.error("Invalid period value")
        return jsonify({"msg": "period must be a non-negative integer"}), 400

    try:
        new_subscription = Subscription(
            type=data['type'],
            price=data['price'],
            period=data['period']
        )

        db.session.add(new_subscription)
        db.session.commit()

        logging.info(f"Subscription added successfully")
        return jsonify({"msg": "Subscription added successfully"}), 201

    except Exception as e:
        db.session.rollback()

        logging.error(f"An error occurred while adding subscription: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@subscription_routes.route('/update_subscription/<int:subscription_id>', methods=['PUT'])
@role_required(["manager"])
def update_subscription(subscription_id):
    data = request.get_json()

    if not data:
        logging.error("No data provided for updating a subscription")
        return jsonify({"msg": "No data provided"}), 400

    subscription = Subscription.query.get(subscription_id)

    if not subscription:
        logging.warning(f"Subscription with ID {subscription_id} does not exist")
        return jsonify({"msg": "Subscription does not exist"}), 404

    allowed_fields = {'type', 'price', 'period'}

    for key, value in data.items():
        if key not in allowed_fields:
            logging.error(f"Field '{key}' is not allowed for update")
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400
        setattr(subscription, key, value)

    try:
        db.session.commit()

        logging.info(f"Subscription updated successfully: ID {subscription_id}")
        return jsonify({"msg": "Subscription updated successfully"}), 200
    
    except Exception as e:
        db.session.rollback()

        logging.error(f"An error occurred while updating subscription: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@subscription_routes.route('/delete_subscription/<int:subscription_id>', methods=['DELETE'])
@role_required(["manager"])
def delete_subscription(subscription_id):
    try:
        subscription = Subscription.query.get(subscription_id)

        if not subscription:
            logging.warning(f"Subscription with ID {subscription_id} does not exist")
            return jsonify({"msg": "Subscription does not exist"}), 404

        customers_with_subscription = Customer.query.filter_by(subscription_id=subscription_id).all()
        for customer in customers_with_subscription:
            customer.subscription_id = None

        db.session.commit()

        db.session.delete(subscription)
        db.session.commit()

        logging.info(f"Subscription {subscription_id} and associated customer links cleared successfully")
        return jsonify({"msg": "Subscription deleted successfully"}), 200
    
    except Exception as e:
        db.session.rollback()

        logging.error(f"An error occurred while deleting subscription: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@subscription_routes.route('/get_subscription/<int:subscription_id>', methods=['GET'])
@role_required(["manager", "receptionist", "coach"])
def get_subscription(subscription_id):
    try:
        subscription = Subscription.query.get(subscription_id)

        if not subscription:
            logging.warning(f"Subscription with ID {subscription_id} does not exist")
            return jsonify({"msg": "Subscription does not exist"}), 404

        result = {
            "subscription_id": subscription.subscription_id,
            "type": subscription.type,
            "price": float(subscription.price),
            "period": subscription.period
        }

        logging.info(f"Subscription retrieved successfully: ID {subscription_id}")
        return jsonify(result), 200
    
    except Exception as e:
        logging.error(f"An error occurred while retrieving subscription: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@subscription_routes.route('/get_all_subscriptions', methods=['GET'])
@role_required(["manager", "receptionist", "coach"])
def get_all_subscriptions():
    try:
        limit = request.args.get('limit', 5, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        subscriptions = Subscription.query.order_by(Subscription.subscription_id).limit(limit).offset(offset).all()

        result = [
            {
                "subscription_id": subscription.subscription_id,
                "type": subscription.type,
                "price": float(subscription.price),
                "period": subscription.period,
            }
            for subscription in subscriptions
        ]
        logging.info("All subscriptions retrieved successfully")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving all subscriptions: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
