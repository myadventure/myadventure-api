"""
DeLorme model

"""

from mongoengine import EmbeddedDocument
from mongoengine import fields

class Delorme(EmbeddedDocument):
    """A DeLorme inReach config.

    """
    feed_url = fields.StringField()
