from flask import Blueprint, request, jsonify
from app.models import Product
from app import db
import logging

# Konfiguracja logowania błędów
logging.basicConfig(level=logging.ERROR)

# Blueprint dla tras związanych z produktami
product_routes = Blueprint('product_routes', __name__)


# Funkcja dodawania produktu
@product_routes.route('/api/add_product', methods=['POST'])
def add_product():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    required_fields = {'product_id', 'gym_id', 'name', 'quantity_in_stock', 'quantity_sold', 'price', 'total_revenue'}
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Field '{field}' is required"}), 400

    if not isinstance(data['product_id'], int) or data['product_id'] <= 0:
        return jsonify({"msg": "product_id must be a positive integer"}), 400
    if not isinstance(data['gym_id'], int) or data['gym_id'] <= 0:
        return jsonify({"msg": "gym_id must be a positive integer"}), 400
    if not isinstance(data['quantity_in_stock'], int) or data['quantity_in_stock'] < 0:
        return jsonify({"msg": "quantity_in_stock must be a non-negative integer"}), 400
    if not isinstance(data['quantity_sold'], int) or data['quantity_sold'] < 0:
        return jsonify({"msg": "quantity_sold must be a non-negative integer"}), 400
    if not isinstance(data['price'], (float, int)) or data['price'] < 0:
        return jsonify({"msg": "price must be a positive number"}), 400

    product = Product.query.get(data['product_id'])
    if product:
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
        return jsonify({"msg": "Product added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while adding product: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@product_routes.route('/api/update_product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "Product does not exist"}), 404

    allowed_fields = {'gym_id', 'name', 'quantity_in_stock', 'quantity_sold', 'price', 'total_revenue'}
    for key, value in data.items():
        if key not in allowed_fields:
            return jsonify({"msg": f"Field '{key}' is not allowed for update"}), 400
        setattr(product, key, value)

    try:
        db.session.commit()
        return jsonify({"msg": "Product updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating product: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@product_routes.route('/api/delete_product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"msg": "Product does not exist"}), 404

        db.session.delete(product)
        db.session.commit()
        return jsonify({"msg": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while deleting product: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500


@product_routes.route('/api/get_product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"msg": "Product does not exist"}), 404

        result = {
            "product_id": product.product_id,
            "gym_id": product.gym_id,
            "name": product.name,
            "quantity_in_stock": product.quantity_in_stock,
            "quantity_sold": product.quantity_sold,
            "price": float(product.price),
            "total_revenue": float(product.total_revenue) if product.total_revenue else 0.0
        }
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred while retrieving product: {str(e)}")
        return jsonify({"msg": "An internal error occurred"}), 500
