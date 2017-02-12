"""
Point model

"""

from mongoengine import EmbeddedDocument
from mongoengine import fields
from .user import User

class Point(EmbeddedDocument):
    """A point.

    """
    point_id = fields.SequenceField()
    title = fields.StringField()
    desc = fields.StringField()
    altitude = fields.StringField()
    speed = fields.StringField()
    direction = fields.StringField()
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    resource = fields.StringField()
    point_type = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True)
    delorme_id = fields.IntField()
    aio_id = fields.IntField()
    instagram_id = fields.StringField()
    hide = fields.BooleanField(default=False)
    thumb = fields.StringField()
    photo = fields.StringField()
    video = fields.StringField()
    source = fields.StringField()
    battery = fields.FloatField()
    user = fields.ReferenceField(User)
    elevation = fields.StringField() # TODO: depracated field

    def to_dict(self):
        """Convert object to dict."""
        result = self.to_mongo().to_dict()
        result['timestamp'] = result['timestamp'].strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return result
