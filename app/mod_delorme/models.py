"""
models.py

Delorme module MongoEngine models
"""

from mongoengine import Document
from mongoengine import fields


class Delorme(Document):
    """A Delorme tracker.

    :param str url: tracker url

    """
    url = fields.StringField(null=False)
