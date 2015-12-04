"""
controllers.py

User module controllers.
"""
from flask import Blueprint, request, jsonify, session
from mongoengine import DoesNotExist

from app.mod_auth import oauth

from app.mod_user.models import User

mod_user = Blueprint('user', __name__, url_prefix='/api/v1/user')


def current_user():
    if 'id' in session:
        uid = session['id']
        try:
            user = User.objects.get(id=uid)
            return user
        except DoesNotExist:
            pass

    return None


@mod_user.route('/')
@oauth.require_oauth()
def me():
    user = request.oauth.user
    return jsonify(email=user.email)