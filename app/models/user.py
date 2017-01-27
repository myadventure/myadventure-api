"""
models.py

User mongoengine models..
"""

import hashlib
from mongoengine import Document
from mongoengine import fields


class User(Document):
    """A platform user.

    :param str email: email address of user
    :param int facebook_id: user's facebook id
    :param str name: user's full name
    :param str facebook_access_token: user's facebook access token
    """
    user_id = fields.SequenceField(primary_key=True)
    email = fields.StringField(unique=True)
    facebook_id = fields.IntField(unique=True, sparse=True)
    name = fields.StringField()
    salt = fields.StringField()
    password = fields.StringField()
    facebook_access_token = fields.StringField()

    def validate_password(self, password):
        """Validate user password."""
        hashed_password = hashlib.sha512(password + self.salt).hexdigest()
        if self.password == hashed_password:
            return True
        return False

    @property
    def is_active(self):
        """Check if user is active."""
        return True

    @property
    def is_authenticated(self):
        """Check if user is authentiacated."""
        return True

    @property
    def is_anonymous(self):
        """Check if user is anonymous."""
        return False

    def get_id(self):
        """Get user id."""
        try:
            return unicode(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')
