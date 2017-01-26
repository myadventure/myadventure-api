"""
Point model

"""

from mongoengine import EmbeddedDocument
from mongoengine import fields

class Point(EmbeddedDocument):
    """A point.

    """
    point_id = fields.SequenceField()
    title = fields.StringField()
    desc = fields.StringField()
    elevation = fields.StringField()
    speed = fields.StringField()
    direction = fields.StringField()
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    resource = fields.StringField()
    point_type = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True)
    delorme_id = fields.IntField()
    hide = fields.BooleanField(default=False)
    thumb = fields.StringField()
    photo = fields.StringField()
    video = fields.StringField()

    def to_dict(self):
        """Convert object to dict."""
        result = self.to_mongo().to_dict()
        result['timestamp'] = result['timestamp'].strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return result
