"""
models.py

Point module MongoEngine models
"""

from mongoengine import Document
from mongoengine import fields

from app.mod_adventure.models import Adventure


class Point(Document):
    title = fields.StringField()
    desc = fields.StringField()
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    resource = fields.StringField()
    type = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True)
    pointid = fields.IntField()
    hide = fields.BooleanField(default=False)
    thumb = fields.StringField()
    photo = fields.StringField()
    video = fields.StringField()
    adventure = fields.ReferenceField(Adventure)

    def to_dict(self):
        result = self.to_mongo()
        result['id'] = str(result['_id'])
        del result['_id']
        timestamp = getattr(self, 'timestamp', None)
        result['timestamp'] = None
        if timestamp:
            result['timestamp'] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        return result
