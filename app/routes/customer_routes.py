from flask import Blueprint, request, jsonify
from app.models import Customer, Subscription
from app import db
import logging
from datetime import datetime, date, timedelta

customer_routes = Blueprint('customer_routes', __name__)


@customer_routes.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.get_json()

    if not data:
        logging.error("No data provided for adding a customer")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'customer_id', 'subscription_id', 'first_name', 'last_name', 'address', 'phone_number', 'sub_purchase_date'}
    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['customer_id'], int) or data['customer_id'] <= 0:
        logging.error("Invalid customer_id provided")
        return jsonify({"msg": "customer_id must be a positive integer"}), 400
    if not isinstance(data['subscription_id'], int):
        logging.error("Invalid subscription_id provided")
        return jsonify({"msg": "subscription_id must be an integer"}), 400

    customer = Customer.query.filter_by(customer_id=data['customer_id']).first()
    if customer:
        logging.warning(f"Customer with ID {data['customer_id']} already exists")
        return jsonify({"msg": "Customer already exists"}), 400

    try:
        new_customer = Customer(
            customer_id=data['customer_id'],
            subscription_id=data['subscription_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            address=data['address'],
            phone_number=data['phone_number'],
            sub_purchase_date=data['sub_purchase_date']
        )
        db.session.add(new_customer)
        db.session.commit()
        logging.info(f"Customer added successfully: ID {data['customer_id']}")
        return jsonify({"msg": "Customer added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while adding a customer: {str(e)}")
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500

@customer_routes.route('/update_customer/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()

    if not data:
        logging.error("No data provided for updating a customer")
        return jsonify({"msg": "No data provided"}), 400

    customer = Customer.query.get(customer_id)
    if not customer:
        logging.warning(f"Customer with ID {customer_id} does not exist")
        return jsonify({"msg": "Customer does not exist"}), 404

    allowed_fields = {'subscription_id', 'first_name', 'last_name', 'address', 'phone_number', 'sub_purchase_date'}
    for key, value in data.items():
        if key not in allowed_fields:
            logging.error(f"Field '{key}' is not allowed for update")
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400
        setattr(customer, key, value)

    try:
        db.session.commit()
        logging.info(f"Customer updated successfully: ID {customer_id}")
        return jsonify({"msg": "Customer updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating a customer: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@customer_routes.route('/delete_customer/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            logging.warning(f"Customer with ID {customer_id} does not exist")
            return jsonify({"msg": "Customer does not exist"}), 404

        db.session.delete(customer)
        db.session.commit()
        logging.info(f"Customer deleted successfully: ID {customer_id}")
        return jsonify({"msg": "Customer deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while deleting a customer: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@customer_routes.route('/get_customer/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        logging.warning(f"Customer with ID {customer_id} does not exist")
        return jsonify({"msg": "Customer does not exist"}), 404

    result = {
        "customer_id": customer.customer_id,
        "subscription_id": customer.subscription_id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "address": customer.address,
        "phone_number": customer.phone_number,
        "sub_purchase_date": str(customer.sub_purchase_date),  
    }
    logging.info(f"Customer retrieved successfully: ID {customer_id}")
    return jsonify(result), 200


@customer_routes.route('/check_sub_validity/<int:customer_id>', methods=['GET'])
def check_sub_validity(customer_id):
    customer = Customer.query.get(customer_id)

    if not customer:
        logging.warning(f"Customer with ID {customer_id} does not exist")
        return jsonify({"msg": "Customer does not exist"}), 404
    
    today = date.today()
    subscription = Subscription.query.filter_by(subscription_id=customer.subscription_id).first()
    if not subscription:
        logging.warning(f"Subscription with ID {customer.subscription_id} does not exist")
        return jsonify({"msg": "Subscription does not exist"}), 404

    period_days = int(subscription.period)
    expiry_date = customer.sub_purchase_date + timedelta(days=period_days)

    if today <= expiry_date:
        logging.info(f"Subscription is valid for customer ID {customer_id}")
        return jsonify({'msg': 'Subscription is valid'}), 200
    else:
        logging.info(f"Subscription expired for customer ID {customer_id}")
        return jsonify({'msg': 'Subscription is no longer valid'}), 401