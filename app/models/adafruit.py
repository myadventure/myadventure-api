"""
adafruit.py

Adafruit mongoengine model

"""

from mongoengine import EmbeddedDocument
from mongoengine import fields

class Adafruit(EmbeddedDocument):
    """A adafruit.io model."""
    base_url = fields.StringField(required=True)
    username = fields.StringField(required=True)
    feed = fields.StringField(required=True)
    aio_key = fields.StringField(required=True)

    def to_dict(self):
        """Convert object to dict."""
        result = self.to_mongo().to_dict()

        return result
