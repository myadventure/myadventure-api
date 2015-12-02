"""
models.py

Point module MongoEngine models
"""

from mongoengine import Document
from mongoengine.fields import *


class Point(Document):
    title = StringField()
    desc = StringField()
    latitude = FloatField()
    longitude = FloatField()
    resource = StringField()
    type = StringField(required=True)
    timestamp = DateTimeField(required=True)
    pointid = IntField()
    hide = BooleanField(default=False)
    thumb = StringField()
    photo = StringField()
    video = StringField()

    def to_dict(self):
        result = self.to_mongo()
        result['id'] = str(result['_id'])
        del result['_id']
        timestamp = getattr(self, 'timestamp', None)
        result['timestamp'] = None
        if timestamp:
            result['timestamp'] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        return result
