from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from dotenv import load_dotenv
from os import getenv
import logging

load_dotenv()

logging.basicConfig(
    #filename='app.log',
    #filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

jwt = JWTManager()
db = SQLAlchemy()
DB_NAME = 'database.db'


def create_database(app):
   with app.app_context():
        db.create_all()
        db.session.commit()


def create_app():
    app = Flask(__name__)
    
    CORS(app)
    CORS(app, origins=["http://localhost:5173"])

    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')

    db.init_app(app)

    app.config['JWT_SECRET_KEY'] = 'secret'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    
    jwt.init_app(app)

    from .auth import auth
    from .routes.customer_routes import customer_routes
    from .routes.employee_routes import employee_routes
    from .routes.gym_routes import gym_routes
    from .routes.gymclass_routes import gymclass_routes
    from .routes.product_routes import product_routes
    from .routes.schedule_routes import schedule_routes
    from .routes.subscription_routes import subscription_routes

    app.register_blueprint(auth, url_prefix='/api')
    app.register_blueprint(customer_routes, url_prefix='/api')
    app.register_blueprint(employee_routes, url_prefix='/api')
    app.register_blueprint(gym_routes, url_prefix='/api')
    app.register_blueprint(gymclass_routes, url_prefix='/api')
    app.register_blueprint(product_routes, url_prefix='/api')
    app.register_blueprint(schedule_routes, url_prefix='/api')
    app.register_blueprint(subscription_routes, url_prefix='/api')

    from . import models

    create_database(app)

    migrate = Migrate(app, db)
    
    return app
