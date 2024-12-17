from flask import Blueprint, request, jsonify
from app import db
from sqlalchemy import text
from models import Customer, Subscription, Employee, Gym, GymClass
routes = Blueprint('routes', __name__)


@routes.route('/')
def home():
    try:
        result = db.session.execute(text('SELECT 1'))
        return "Database connection successful!", 200
    except Exception as e:
        return f"Error: {e}", 500
    
@routes.route('/api/add_customer', methods=['POST'])
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

@routes.route('/api/update_customer/<int:customer_id>', methods=['PUT'])
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

@routes.route('/api/delete_customer/<int:customer_id>', methods=['DELETE'])
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
    
@routes.route('/api/get_customer/<int:customer_id>', methods=['GET'])
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

@routes.route('/api/add_gym', methods=['POST'])
def add_gym():
    data = request.get_json()

    gym_id = data['gym_id']
    name = data['name']
    address = data['address']

    gym = Gym.query.filter_by(gym_id=gym_id).first()
    if gym:
        return jsonify({"msg": "Gym already exists"}), 400
    
    try:
        new_gym = Gym(
            gym_id=gym_id,
            name=name,
            address=address,
        )
        db.session.add(new_gym)
        db.session.commit()
        return jsonify({"msg": "Gym added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    
@routes.route('/api/get_gym/<int:gym_id>', methods=['GET'])
def get_gym(gym_id):
    gym = Gym.query.get(gym_id)
    if not gym:
        return jsonify({"msg": "Gym does not exist"}), 404

    result = {
        "gym_id": gym.gym_id,
        "name": gym.name,
        "address": gym.address,
    }
    return jsonify(result), 200