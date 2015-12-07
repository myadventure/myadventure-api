"""
models.py

Adventure module MongoEngine models
"""

from mongoengine import Document
from mongoengine import fields

from app.mod_delorme.models import Delorme


class Adventure(Document):
    """An adventure.

    :param str name: adventure display name
    :param str slug: adventure slug for urls
    :param ref delorme: reference to a Delorme tracker

    """
    name = fields.StringField()
    slug = fields.StringField(unique=True)
    delorme = fields.ReferenceField(Delorme)

