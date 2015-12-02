"""
models.py

User module MongoEngine models
"""

from mongoengine import Document
from mongoengine.fields import *


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
