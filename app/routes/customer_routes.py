from flask import Blueprint, request, jsonify
from app.models import Customer, Subscription
from app import db
import logging
from datetime import datetime, date, timedelta
from utils import role_required

customer_routes = Blueprint('customer_routes', __name__)


@customer_routes.route('/add_customer', methods=['POST'])
@role_required(["manager", "receptionist"])
def add_customer():
    data = request.get_json()

    if not data:
        logging.error("No data provided for adding a customer")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'first_name', 'last_name', 'address', 'phone_number'}

    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if 'customer_id' in data and (not isinstance(data['customer_id'], int) or data['customer_id'] <= 0):
        logging.error("Invalid customer_id provided")
        return jsonify({"msg": "customer_id must be a positive integer"}), 400
    
    if 'subscription_id' in data and (data['subscription_id'] and not isinstance(data['subscription_id'], int)):
        logging.error("Invalid subscription_id provided")
        return jsonify({"msg": "subscription_id must be an integer"}), 400

    subscription_id = data.get("subscription_id")

    if subscription_id is not None:
        subscription_exists = db.session.query(
            db.session.query(Subscription).filter_by(subscription_id=subscription_id).exists()
        ).scalar()
        
        if not subscription_exists:
            logging.error(f"subscription_id {subscription_id} does not exist")
            return jsonify({"msg": f"subscription_id {subscription_id} does not exist"}), 400
        
    
    if 'sub_purchase_date' in data and data['sub_purchase_date'] is not None:
        try:
            data['sub_purchase_date'] = datetime.strptime(data['sub_purchase_date'], '%Y-%m-%d')
        except ValueError:
            logging.error("Invalid date format for sub_purchase_date")
            return jsonify({"msg": "sub_purchase_date must be in the format 'YYYY-MM-DD'"}), 400
        
    try:
        new_customer = Customer(
            subscription_id=data.get('subscription_id'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            address=data['address'],
            phone_number=data['phone_number'],
            sub_purchase_date=data.get('sub_purchase_date')
        )

        db.session.add(new_customer)
        db.session.commit()

        logging.info(f"Customer added successfully")

        return jsonify({"msg": "Customer added successfully"}), 201

    except Exception as e:
        db.session.rollback()

        logging.error(f"An error occurred while adding a customer: {str(e)}")
        logging.error(f"An error occurred: {str(e)}")

        return jsonify({"msg": "An internal error occurred"}), 500


@customer_routes.route('/update_customer/<int:customer_id>', methods=['PUT'])
@role_required(["manager", "receptionist"])
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
@role_required(["manager", "receptionist"])
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
@role_required(["manager", "receptionist", "coach"])
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
@role_required(["manager", "receptionist"])
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
 
    
@customer_routes.route('/get_all_customers', methods=['GET'])
@role_required(["manager", "receptionist", "coach"])
def get_all_customers():
    try:
        customers = Customer.query.all()
        result = [
            {
                "customer_id": customer.customer_id,
                "subscription_id": customer.subscription_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "address": customer.address,
                "phone_number": customer.phone_number,
                "sub_purchase_date": str(customer.sub_purchase_date),
            }
            for customer in customers
        ]
        logging.info("All customers retrieved successfully")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving all customers: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500