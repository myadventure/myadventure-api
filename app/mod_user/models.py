"""
models.py

User module MongoEngine models
"""

from mongoengine import Document
from mongoengine import fields


class User(Document):
    """A platform user.

    :param str email: email address of user

    """

    email = fields.StringField(required=True, primary_key=True)
    # password = fields.StringField(required=True)
    # salt = fields.StringField(required=True)
    authenticated = fields.BooleanField(default=False)

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
