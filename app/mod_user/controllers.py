"""
controllers.py

User module controllers.
"""
from flask import logging, Blueprint
from mongoengine import DoesNotExist
from flask import session

from app.mod_user.models import User

mod_user = Blueprint('user', __name__, url_prefix='/user')


def current_user():
    if 'id' in session:
        uid = session['id']
        try:
            user = User.objects.get(id=uid)
            return user
        except DoesNotExist:
            logging.info("User not found.")
    return None
