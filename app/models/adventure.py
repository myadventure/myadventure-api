"""
Adventure model

"""

from mongoengine import Document
from mongoengine import fields
from app.models.user import User
from .delorme import Delorme
from .adafruit import Adafruit
from .point import Point


class Adventure(Document):
    """An adventure.

    :param str slug: adventure slug for urls
    :param str name: adventure display name
    :param arr users: a list of users who have access to the adventure
    :param ref delorme: reference to a Delorme embedded document
    :param ref points: list of references to Point embedded documents

    """
    slug = fields.StringField(primary_key=True)
    name = fields.StringField()
    users = fields.ListField(fields.ReferenceField(User))
    delorme = fields.EmbeddedDocumentField(Delorme)
    adafruit = fields.EmbeddedDocumentField(Adafruit)
    points = fields.EmbeddedDocumentListField(Point)


    def to_dict(self):
        """Convert object to dict."""
        result = self.to_mongo().to_dict()
        if 'points' in result.keys():
            del result['points']
        if 'delorme' in result.keys():
            del result['delorme']

        return result
