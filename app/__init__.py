from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from dotenv import load_dotenv
from os import getenv

load_dotenv()

jwt = JWTManager()
db = SQLAlchemy()
DB_NAME = 'database.db'


def create_database(app):
   with app.app_context():
        db.create_all()
        db.session.commit()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'chudeszczury1'
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')

    db.init_app(app)

    app.config['JWT_SECRET_KEY'] = 'chudeszczury2'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    
    jwt.init_app(app)

    from .routes import routes
    from .auth import auth

    app.register_blueprint(routes, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from . import models

    create_database(app)

    migrate = Migrate(app, db)
    
    return app
