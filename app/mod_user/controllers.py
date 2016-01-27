"""
controllers.py

User module controllers.
"""
import hashlib
import logging

from flask import Blueprint, request, jsonify, abort
from mongoengine import NotUniqueError
from werkzeug.security import gen_salt

from app.mod_auth.controllers import oauth
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
        return jsonify({"user": user.to_mongo()})
    except TypeError:
        abort(400)
    except Exception as e:
        logging.error(e.args[0])
        abort(500)
