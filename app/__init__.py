"""
Initialize application

"""
import os
import logging
from mongoengine import connect
from flask import Flask, jsonify
from app.views.auth import MOD_AUTH
from app.views.auth import OAUTH
from app.views.user import MOD_USER
from .views.adventure import MOD_ADVENTURE
from .views.delorme import MOD_DELORME
from .views.point import MOD_POINT
from .views.adafruit import MOD_ADAFRUIT
from .views.android import MOD_ANDROID
from .views.instagram import MOD_INSTAGRAM

APP = Flask(__name__, static_folder=os.getcwd() \
    + '/app/static', static_url_path='', template_folder=os.getcwd() \
    + '/app/templates' \
)

APP.config.from_pyfile('config.py', silent=True)

connect(
    host=APP.config['MONGODB_URI']
)

OAUTH.init_app(APP)


@APP.errorhandler(400)
def bad_request(err):
    """Return a custom 400 error."""
    logging.error(err)
    return jsonify( \
        error='The browser (or proxy) sent a request that this server could not understand.' \
    ), 400


@APP.errorhandler(404)
def page_not_found(err):
    """Return a custom 404 error."""
    logging.error(err)
    return jsonify(error='Sorry, Nothing at this URL.'), 404


@APP.errorhandler(500)
def internal_error(err):
    """Return a custom 500 error."""
    return jsonify(error='Sorry, unexpected error: {}'.format(err)), 500

# Registering module blueprints
APP.register_blueprint(MOD_AUTH)
APP.register_blueprint(MOD_USER)
APP.register_blueprint(MOD_ADVENTURE)
APP.register_blueprint(MOD_DELORME)
APP.register_blueprint(MOD_POINT)
APP.register_blueprint(MOD_ADAFRUIT)
APP.register_blueprint(MOD_ANDROID)
APP.register_blueprint(MOD_INSTAGRAM)
