"""
Initialize user module

"""
from flask import session
from mongoengine import DoesNotExist

from app.mod_user.models import User


def current_user():
    if 'facebook_id' in session:
        facebook_id = session['facebook_id']
        try:
            user = User.objects.get(facebook_id=facebook_id)
            return user
        except DoesNotExist:
            pass

    return None
