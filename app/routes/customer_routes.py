from flask import Blueprint, request, jsonify
from app import db
from sqlalchemy import text
from app.models import Customer, Subscription, Employee, Gym, GymClass

customer = Blueprint('customer', __name__)


@customer.route('/api/add_customer', methods=['POST'])
def add_customer():
    data = request.get_json()

    customer_id = data['customer_id']
    subscription_id = data['subscription_id']
    first_name = data['first_name']
    last_name = data['last_name']
    address = data['address']
    phone_number = data['phone_number']
    sub_purchase_date = data['sub_purchase_date']

    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if customer:
        return jsonify({"msg": "Customer already exists"}), 400
    
    try:
        new_customer = Customer(
            customer_id=customer_id,
            subscription_id=subscription_id,
            first_name=first_name,
            last_name=last_name,
            address=address,
            phone_number=phone_number,
            sub_purchase_date=sub_purchase_date
        )
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"msg": "Customer added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    

@customer.route('/api/update_customer/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()

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
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    

@customer.route('/api/delete_customer/<int:customer_id>', methods=['DELETE'])
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
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500


@customer.route('/api/get_customer/<int:customer_id>', methods=['GET'])
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
        "sub_purchase_date": customer.sub_purchase_date,
    }
    
    return jsonify(result), 200