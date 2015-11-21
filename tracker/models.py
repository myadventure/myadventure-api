"""
models.py

App Engine datastore models

"""

from mongoengine import Document
from mongoengine.fields import *
import logging
import datetime
import bson

class Point(Document):
    title = StringField()
    desc = StringField()
    latitude = FloatField()
    longitude = FloatField()
    resource = StringField()
    type = StringField(required=True)
    timestamp = DateTimeField(required=True)
    pointid = IntField()
    hide = BooleanField(default=False)
    thumb = StringField()
    photo = StringField()
    video = StringField()

    def to_dict(self):
        result = self.to_mongo()
        result['id'] = str(result['_id'])
        del result['_id']
        timestamp = getattr(self, 'timestamp', None)
        result['timestamp'] = None
        if timestamp:
            result['timestamp'] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        return result


class Config(Document):
    name = StringField(required=True)
    value = StringField(required=True)
    date_added = DateTimeField(default=datetime.datetime.now())

    def to_dict(self):
        result = self.to_mongo()
        del result['date_added']
        return result


class User(Document):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """

    email = StringField(required=True, primary_key=True)
    password = StringField(required=True)
    salt = StringField(required=True)
    authenticated = BooleanField(default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
