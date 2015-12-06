"""
controllers.py

User module controllers.
"""
from flask import Blueprint, request, jsonify

from app.mod_auth import oauth

mod_user = Blueprint('user', __name__, url_prefix='/api/v1/user')


@mod_user.route('/')
@oauth.require_oauth('email')
def me():
    user = request.oauth.user
    return jsonify(email=user.email)