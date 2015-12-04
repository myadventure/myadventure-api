"""
models.py

User module MongoEngine models
"""

from mongoengine import Document
from mongoengine import fields


class User(Document):
    """A platform user.

    :param str username: username of user
    :param str email: email address of user

    """
    id = fields.SequenceField(primary_key=True)
    username = fields.StringField(unique=True)
    email = fields.StringField()