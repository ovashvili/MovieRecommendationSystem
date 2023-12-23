from flask import Flask, request, jsonify, make_response
from flask_restful import Api
import numpy as np
import pandas as pd
from flask_swagger_ui import get_swaggerui_blueprint
# from flask_sqlalchemy import SQLAlchemy
from routes import movies_api

APP = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Movies Recommendation API"
    }
)

APP.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

APP.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

APP.register_blueprint(movies_api.get_blueprint())


@APP.errorhandler(400)
def handle_400_error(_error):
    """Return a http 400 error to client"""
    return make_response(jsonify({'error': 'Misunderstood'}), 400)


@APP.errorhandler(401)
def handle_401_error(_error):
    """Return a http 401 error to client"""
    return make_response(jsonify({'error': 'Unauthorised'}), 401)


@APP.errorhandler(404)
def handle_404_error(_error):
    """Return a http 404 error to client"""
    return make_response(jsonify({'error': 'Not found'}), 404)


@APP.errorhandler(500)
def handle_500_error(_error):
    """Return a http 500 error to client"""
    return make_response(jsonify({'error': 'Server error'}), 500)

#api = Api(APP)

