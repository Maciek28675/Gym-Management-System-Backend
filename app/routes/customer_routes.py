from flask import Blueprint, request, jsonify
from app.models import Customer, Subscription
from app import db
import logging
from datetime import datetime, date, timedelta

logging.basicConfig(level=logging.ERROR)

customer_routes = Blueprint('customer_routes', __name__)


@customer_routes.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'customer_id', 'subscription_id', 'first_name', 'last_name', 'address', 'phone_number', 'sub_purchase_date'}
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['customer_id'], int) or data['customer_id'] <= 0:
        return jsonify({"msg": "customer_id must be a positive integer"}), 400
    if not isinstance(data['subscription_id'], int):
        return jsonify({"msg": "subscription_id must be an integer"}), 400

    customer = Customer.query.filter_by(customer_id=data['customer_id']).first()
    if customer:
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
        return jsonify({"msg": "Customer added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@customer_routes.route('/update_customer/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"msg": "Customer does not exist"}), 404

    allowed_fields = {'subscription_id', 'first_name', 'last_name', 'address', 'phone_number', 'sub_purchase_date'}
    for key, value in data.items():
        if key not in allowed_fields:
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400
        setattr(customer, key, value)

    try:
        db.session.commit()
        return jsonify({"msg": "Customer updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@customer_routes.route('/delete_customer/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"msg": "Customer does not exist"}), 404

        db.session.delete(customer)
        db.session.commit()
        return jsonify({"msg": "Customer deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@customer_routes.route('/get_customer/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
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
    return jsonify(result), 200


@customer_routes.route('/check_sub_validity/<int:customer_id>', methods=['GET'])
def check_sub_validity(customer_id):
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({"msg": "Customer does not exist"}), 404
    
    result = {
        "subscription_id": customer.subscription_id,
        "sub_purchase_date": customer.sub_purchase_date
    }

    today = datetime.date.today()
    period = Subscription.query.with_entities(Subscription.period).filter_by(id=customer.subscription_id).first()

    if timedelta(today - customer.sub_purchase_date) < timedelta(period):
        return jsonify({'msg': 'Subscription is valid'}), 200
    else:
        return jsonify({'msg': 'Subscription is no longer valid'}), 401
    
