"""
models.py

Config module MongoEngine models
"""

from mongoengine import Document
from mongoengine.fields import *
import logging
import datetime
import bson

class Config(Document):
    name = StringField(required=True)
    value = StringField(required=True)
    date_added = DateTimeField(default=datetime.datetime.now())

    def to_dict(self):
        result = self.to_mongo()
        result['id'] = str(result['_id'])
        del result['_id']
        del result['date_added']
        return result
