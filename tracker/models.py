"""
models.py

App Engine datastore models

"""

from google.appengine.ext import ndb
import logging

class Point(ndb.Model):
    title = ndb.StringProperty()
    desc = ndb.StringProperty()
    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()
    resource = ndb.StringProperty()
    type = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(required=True)
    pointid = ndb.IntegerProperty()
    hide = ndb.BooleanProperty(default=False)
    thumb = ndb.StringProperty()
    photo = ndb.StringProperty()
    video = ndb.StringProperty()

    @classmethod
    def delete_all(cls, delete_type):
        ndb.delete_multi(
            cls.query(cls.type == delete_type).fetch(keys_only=True)
        )
        return True

    def to_dict(self):
        result = super(Point,self).to_dict()
        result['id'] = self.key.id()
        timestamp = getattr(self, 'timestamp', None)
        result['timestamp'] = None
        if timestamp:
            result['timestamp'] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        return result


class Config(ndb.Model):
    name = ndb.StringProperty(required=True)
    value = ndb.StringProperty(required=True)
    date_added = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        result = super(Config,self).to_dict()
        del result['date_added']
        return result


class User(ndb.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """

    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    salt = ndb.StringProperty(required=True)
    authenticated = ndb.BooleanProperty(default=False)

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
