from flask import Blueprint, request, jsonify
from app.models import Product
from app import db
import logging

product_routes = Blueprint('product_routes', __name__)


@product_routes.route('/add_product', methods=['POST'])
def add_product():
    data = request.get_json()

    if not data:
        logging.error("No data provided for adding a product")
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'product_id', 'gym_id', 'name', 'quantity_in_stock', 'quantity_sold', 'price', 'total_revenue'}
    for field in required_fields:
        if field not in data:
            logging.error(f"Missing required field: {field}")
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['product_id'], int) or data['product_id'] <= 0:
        logging.error("Invalid product_id")
        return jsonify({"msg": "product_id must be a positive integer"}), 400

    product = Product.query.filter_by(product_id=data['product_id']).first()
    if product:
        logging.error(f"Product with ID {data['product_id']} already exists")
        return jsonify({"msg": "Product already exists"}), 400

    try:
        new_product = Product(
            product_id=data['product_id'],
            gym_id=data['gym_id'],
            name=data['name'],
            quantity_in_stock=data['quantity_in_stock'],
            quantity_sold=data['quantity_sold'],
            price=data['price'],
            total_revenue=data['total_revenue']
        )
        db.session.add(new_product)
        db.session.commit()
        logging.info(f"Product {data['product_id']} added successfully")
        return jsonify({"msg": "Product added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while adding product: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@product_routes.route('/update_product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()

    if not data:
        logging.error("No data provided for updating a product")
        return jsonify({"msg": "No data provided"}), 400

    product = Product.query.get(product_id)
    if not product:
        logging.error(f"Product with ID {product_id} does not exist")
        return jsonify({"msg": "Product does not exist"}), 404

    allowed_fields = {'gym_id', 'name', 'quantity_in_stock', 'quantity_sold', 'price', 'total_revenue'}
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
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            logging.error(f"Product with ID {product_id} does not exist")
            return jsonify({"msg": "Product does not exist"}), 404

        db.session.delete(product)
        db.session.commit()
        logging.info(f"Product {product_id} deleted successfully")
        return jsonify({"msg": "Product deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while deleting product {product_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@product_routes.route('/get_product/<int:product_id>', methods=['GET'])
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


@product_routes.route('/sell_product/<int:product_id>', methods=['POST'])
def sell_product(product_id):
    data = request.get_json()

    if 'quantity_sold' not in data or not isinstance(data['quantity_sold'], int) or data['quantity_sold'] <= 0:
        logging.error("Invalid 'quantity_sold' provided for selling a product")
        return jsonify({"msg": "Valid 'quantity_sold' is required"}), 400

    product = Product.query.get(product_id)
    if not product:
        logging.error(f"Product with ID {product_id} does not exist")
        return jsonify({"msg": "Product does not exist"}), 404

    if product.quantity_in_stock < data['quantity_sold']:
        logging.error(f"Not enough stock for Product {product_id}")
        return jsonify({"msg": "Not enough stock available"}), 400

    try:
        product.quantity_in_stock -= data['quantity_sold']
        product.quantity_sold += data['quantity_sold']
        product.total_revenue += data['quantity_sold'] * float(product.price)

        db.session.commit()
        logging.info(f"Product {product_id} sold successfully. Quantity: {data['quantity_sold']}")
        return jsonify({"msg": "Product sold successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred during product sale for Product {product_id}: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500