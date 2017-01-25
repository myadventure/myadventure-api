"""
Initialize application

"""
import os
from mongoengine import connect
from flask import Flask, jsonify
from app.mod_auth.controllers import mod_auth
from app.mod_user.controllers import MOD_USER
from app.mod_adventure.controllers import MOD_ADVENTURE
from app.mod_user.models import User
from app.mod_auth.controllers import oauth

APP = Flask(__name__, static_folder=os.getcwd() \
    + '/app/static', static_url_path='', template_folder=os.getcwd() \
    + '/app/templates' \
)

APP.config.from_pyfile('config.py', silent=True)

connect(
    host=APP.config['MONGODB_URI']
)

oauth.init_app(APP)


@APP.errorhandler(400)
def bad_request():
    """Return a custom 400 error."""
    return jsonify( \
        error='The browser (or proxy) sent a request that this server could not understand.' \
    ), 400


@APP.errorhandler(404)
def page_not_found():
    """Return a custom 404 error."""
    return jsonify(error='Sorry, Nothing at this URL.'), 404


@APP.errorhandler(500)
def internal_error(err):
    """Return a custom 500 error."""
    return jsonify(error='Sorry, unexpected error: {}'.format(err)), 500

# Registering module blueprints
APP.register_blueprint(mod_auth)
APP.register_blueprint(MOD_USER)
APP.register_blueprint(MOD_ADVENTURE)
