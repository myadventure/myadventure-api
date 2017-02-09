"""
instagram.py

Instagram mongoengine model

"""

from mongoengine import EmbeddedDocument
from mongoengine import fields

class Instagram(EmbeddedDocument):
    """A Instagram model."""
    access_token = fields.StringField(required=True)
    client_secret = fields.StringField(required=True)

    def to_dict(self):
        """Convert object to dict."""
        result = self.to_mongo().to_dict()

        return result
