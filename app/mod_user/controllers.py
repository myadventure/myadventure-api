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

mod_user = Blueprint('user', __name__, url_prefix='/api/v1/user')


@mod_user.route('/', methods=['GET'])
@oauth.require_oauth('email')
def me():
    user = request.oauth.user
    return jsonify(user=user.to_mongo())


@mod_user.route('/', methods=['POST'])
def add_user():
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
    except Exception as e:
        logging.error(e.args[0])
        return abort(500)
