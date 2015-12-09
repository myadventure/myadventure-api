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
    delorme_id = fields.IntField()
    hide = fields.BooleanField(default=False)
    thumb = fields.StringField()
    photo = fields.StringField()
    video = fields.StringField()
    adventure = fields.ReferenceField(Adventure)

    def to_dict(self):
        result = self.to_mongo().to_dict()
        result['timestamp'] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        result['_id'] = str(self.id)

        return result
