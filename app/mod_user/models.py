"""
models.py

User module MongoEngine models
"""

from mongoengine import Document
from mongoengine import fields


class User(Document):
    """A platform user.

    :param str email: email address of user
    :param int facebook_id: user's facebook id
    :param str name: user's full name
    :param str facebook_access_token: user's facebook access token
    """
    id = fields.SequenceField(primary_key=True)
    email = fields.StringField(unique=True)
    facebook_id = fields.IntField(unique=True)
    name = fields.StringField()
    salt = fields.StringField()
    password = fields.StringField()
    facebook_access_token = fields.StringField()
