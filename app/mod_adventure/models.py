"""
models.py

Adventure module MongoEngine models
"""

from mongoengine import Document
from mongoengine import fields

from app.mod_user.models import User
from app.mod_delorme.models import Delorme


class Adventure(Document):
    """An adventure.

    :param str name: adventure display name
    :param str slug: adventure slug for urls
    :param ref delorme: reference to a Delorme tracker

    """
    slug = fields.StringField(primary_key=True)
    name = fields.StringField()
    users = fields.ListField(fields.ReferenceField(User))
    delorme = fields.ReferenceField(Delorme)

    def to_dict(self):
        result = self.to_mongo().to_dict()
        result['_id'] = str(self.id)
        result['delorme'] = str(self.delorme.id)

        return result

