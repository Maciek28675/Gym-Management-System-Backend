from flask import Blueprint

routes = Blueprint('routes', __name__)


@routes.route('/')
def home():
    return '<h1>Welcome to Gym Management 1.0</h1>'
