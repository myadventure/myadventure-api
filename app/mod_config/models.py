"""
models.py

Config module MongoEngine models
"""

from mongoengine import Document
from mongoengine import fields
import datetime


class Config(Document):
    name = fields.StringField(required=True)
    value = fields.StringField(required=True)
    date_added = fields.DateTimeField(default=datetime.datetime.now())

    def to_dict(self):
        result = self.to_mongo()
        result['id'] = str(result['_id'])
        del result['_id']
        del result['date_added']
        return result
