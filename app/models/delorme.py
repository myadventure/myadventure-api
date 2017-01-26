"""
DeLorme model

"""

from mongoengine import EmbeddedDocument
from mongoengine import fields

class Delorme(EmbeddedDocument):
    """A DeLorme inReach config.

    """
    feed_url = fields.StringField()

    def to_dict(self):
        """Convert object to dict."""
        result = self.to_mongo().to_dict()

        return result
