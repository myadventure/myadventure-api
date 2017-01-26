"""
controllers.py

User module controllers.
"""
import hashlib
import logging

from flask import Blueprint, request, jsonify, abort
from mongoengine import NotUniqueError, DoesNotExist
from werkzeug.security import gen_salt

from app.mod_auth.controllers import oauth
from app.mod_auth.models import Client
from app.mod_user.models import User
from app.models.adventure import Adventure
from app.decorators import crossdomain

MOD_USER = Blueprint('user', __name__, url_prefix='/api/v1/user')


@MOD_USER.route('/', methods=['GET'])
@oauth.require_oauth('email')
def get_current_user():
    """Get current user."""
    user = request.oauth.user
    return jsonify(user=user.to_mongo())


@MOD_USER.route('/', methods=['POST'])
def add_user():
    """Add new user."""
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        client_id = request.form.get('client_id')

        try:
            client = Client.objects.get(client_id=client_id)
        except DoesNotExist:
            logging.info("Client not found.")
            return abort(400)

        if not client.has_password_credential_permission:
            return abort(400)

        salt = gen_salt(40)
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        user = User(
            email=email,
            password=hashed_password,
            salt=salt
        )
        user.save()
        return jsonify({"user": user.to_mongo()})
    except NotUniqueError:
        logging.info("Duplicate user.")
        return abort(400)
    except TypeError:
        return abort(400)
    return

@MOD_USER.route('/adventure', methods=['GET'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def list_user_adventures():
    """Return user Adventures."""
    user = request.oauth.user
    adventures = Adventure.objects(users=user)
    adventures_dict = []
    for adventure in adventures:
        adventures_dict.append(adventure.to_dict())
    return jsonify(adventures=adventures_dict)
