"""
controllers.py

User module controllers.
"""
import hashlib
import logging
import traceback

from flask import Blueprint, request, jsonify, abort
from mongoengine import NotUniqueError
from werkzeug.security import gen_salt

from app.mod_auth import oauth
from app.mod_user.models import User

mod_user = Blueprint('user', __name__, url_prefix='/api/v1/user')


@mod_user.route('/', methods=['GET'])
@oauth.require_oauth('email')
def me():
    user = request.oauth.user
    return jsonify(email=user.email)


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
    except TypeError:
        abort(400)
    except NotUniqueError:
        return jsonify({"user": user.to_mongo()})
    except Exception as e:
        logging.error(e.args[0])
        traceback.print_exc()
        abort(500)
