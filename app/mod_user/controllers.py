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
    if 'facebook_id' in session:
        facebook_id = session['facebook_id']
        try:
            user = User.objects.get(facebook_id=facebook_id)
            return user
        except DoesNotExist:
            pass

    return None


@mod_user.route('/')
@oauth.require_oauth('email')
def me():
    user = request.oauth.user
    return jsonify(email=user.email)