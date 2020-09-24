"""
Adventure model

"""

from mongoengine import Document
from mongoengine import fields
from .user import User
from .delorme import Delorme
from .adafruit import Adafruit
from .instagram import Instagram
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
    description = fields.StringField()
    users = fields.ListField(fields.ReferenceField(User))
    delorme = fields.EmbeddedDocumentField(Delorme)
    adafruit = fields.EmbeddedDocumentField(Adafruit)
    instagram = fields.EmbeddedDocumentField(Instagram)
    points = fields.EmbeddedDocumentListField(Point)


    def to_dict(self):
        """Convert object to dict."""
        result = self.to_mongo().to_dict()
        if 'points' in list(result.keys()):
            del result['points']
        if 'delorme' in list(result.keys()):
            del result['delorme']

        return result
