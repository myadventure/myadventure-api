"""
Initialize adventure model

"""

from mongoengine import Document
from mongoengine import fields

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
    points = fields.EmbeddedDocumentListField(Point)


    def to_dict(self):
        """Convert object to dict."""
        result = self.to_mongo().to_dict()
        del result['points']
        del result['_id']

        return result
