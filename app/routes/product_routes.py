from flask import Blueprint, request, jsonify
from app.models import Product
from app import db
import logging
from decimal import Decimal
from utils import role_required
from flask_jwt_extended import get_jwt

product_routes = Blueprint('product_routes', __name__)


@product_routes.route('/add_product', methods=['POST'])
@role_required(["manager", "receptionist"])
def add_product():
    data = request.get_json()

    if not data:
        logging.error("No data provided for adding a product")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'gym_id', 'name', 'quantity_in_stock', 'quantity_sold', 'price', 'total_revenue'}

    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400
        
    jwt_payload = get_jwt()
    user_gym_id = jwt_payload.get('gym_id')

    if user_gym_id != data['gym_id']:
        logging.warning("You are not authorized to modify this gym")
        return jsonify({"msg": "You are not authorized to modify this gym"}), 403

    try:
        new_product = Product(
            gym_id=data['gym_id'],
            name=data['name'],
            quantity_in_stock=data['quantity_in_stock'],
            quantity_sold=data['quantity_sold'],
            price=data['price'],
            total_revenue=data['total_revenue']
        )
        db.session.add(new_product)
        db.session.commit()

        logging.info(f"Product added successfully")
        return jsonify({"msg": "Product added successfully"}), 201

    except Exception as e:
        db.session.rollback()

        logging.error(f"An error occurred while adding product: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@product_routes.route('/update_product/<int:product_id>', methods=['PUT'])
@role_required(["manager", "receptionist"])
def update_product(product_id):
    data = request.get_json()

    if not data:
        logging.error("No data provided for updating a product")
        return jsonify({"msg": "No data provided"}), 400

    product = Product.query.get(product_id)

    if not product:
        logging.error(f"Product with ID {product_id} does not exist")
        return jsonify({"msg": "Product does not exist"}), 404

    allowed_fields = {'name', 'quantity_in_stock', 'price', 'total_revenue'}

    for key, value in data.items():
        if key not in allowed_fields:
            logging.error(f"Field '{key}' is not allowed for update")
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400
        setattr(product, key, value)

    try:
        db.session.commit()

        logging.info(f"Product {product_id} updated successfully")
        return jsonify({"msg": "Product updated successfully"}), 200

    except Exception as e:
        db.session.rollback()

        logging.error(f"An error occurred while updating product {product_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@product_routes.route('/delete_product/<int:product_id>', methods=['DELETE'])
@role_required(["manager", "receptionist"])
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            logging.error(f"Product with ID {product_id} does not exist")
            return jsonify({"msg": "Product does not exist"}), 404
        
        jwt_payload = get_jwt()
        user_gym_id = jwt_payload.get('gym_id')

        if user_gym_id != product.gym_id:
            logging.warning("You are not authorized to modify this gym")
            return jsonify({"msg": "You are not authorized to modify this gym"}), 403

        db.session.delete(product)
        db.session.commit()
        logging.info(f"Product {product_id} deleted successfully")
        return jsonify({"msg": "Product deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while deleting product {product_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@product_routes.route('/get_product/<int:product_id>', methods=['GET'])
@role_required(["manager", "receptionist"])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            logging.error(f"Product with ID {product_id} does not exist")
            return jsonify({"msg": "Product does not exist"}), 404

        result = {
            "product_id": product.product_id,
            "gym_id": product.gym_id,
            "name": product.name,
            "quantity_in_stock": product.quantity_in_stock,
            "quantity_sold": product.quantity_sold,
            "price": float(product.price),
            "total_revenue": float(product.total_revenue),
        }
        logging.info(f"Product {product_id} retrieved successfully")
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"An error occurred while retrieving product {product_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@product_routes.route('/sell_product/<int:product_id>', methods=['PUT'])
@role_required(["manager", "receptionist"])
def sell_product(product_id):
    data = request.get_json()

    product = Product.query.get(product_id)
    quantity_sold = product.quantity_sold

    #if 'quantity_sold' not in data or not isinstance(data['quantity_sold'], int) or data['quantity_sold'] <= 0:
    #    logging.error("Invalid 'quantity_sold' provided for selling a product")
    #    return jsonify({"msg": "Valid 'quantity_sold' is required"}), 400

    
    if not product:
        logging.error(f"Product with ID {product_id} does not exist")
        return jsonify({"msg": "Product does not exist"}), 404

    jwt_payload = get_jwt()
    user_gym_id = jwt_payload.get('gym_id')

    if user_gym_id != product.gym_id:
        logging.warning("You are not authorized to modify this gym")
        return jsonify({"msg": "You are not authorized to modify this gym"}), 403
    
    if product.quantity_in_stock < 1:
        logging.error(f"Not enough stock for Product {product_id}")
        return jsonify({"msg": "Not enough stock available"}), 400

    try:
        product.quantity_in_stock -= 1
        product.quantity_sold += 1
        product.total_revenue += Decimal(product.price)

        db.session.commit()
        logging.info(f"Product {product_id} sold successfully. Quantity: {quantity_sold}")
        return jsonify({"msg": "Product sold successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred during product sale for Product {product_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@product_routes.route('/get_all_products', methods=['GET'])
@role_required(["manager", "receptionist"])
def get_all_products():
    try:

        limit = request.args.get('limit', 5, type=int)
        offset = request.args.get('offset', 0, type=int)

        products = Product.query.order_by(Product.product_id).limit(limit).offset(offset).all()
        result = [
            {
                "product_id": product.product_id,
                "gym_id": product.gym_id,
                "name": product.name,
                "quantity_in_stock": product.quantity_in_stock,
                "quantity_sold": product.quantity_sold,
                "price": float(product.price),
                "total_revenue": float(product.total_revenue),
            }
            for product in products
        ]
        logging.info("All products retrieved successfully")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving all products: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
