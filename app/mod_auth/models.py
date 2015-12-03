"""
models.py

Auth module MongoEngine models
"""

from mongoengine import Document
from mongoengine import fields


class User(Document):
    """A platform user.

    :param str username: username of user
    :param str email: email address of user

    """
    id = fields.SequenceField(primary_key=True)
    username = fields.StringField(unique=True)
    email = fields.StringField()


class Client(Document):
    user_id = fields.IntField(null=False)
    user = fields.ReferenceField(User)

    client_id = fields.StringField(primary_key=True)
    client_secret = fields.StringField(null=False, unique=True)

    # public or confidential
    is_confidential = fields.BooleanField()

    _redirect_uris = fields.StringField()
    _default_scopes = fields.StringField()

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []


class Grant(Document):
    id = fields.SequenceField(primary_key=True)

    user_id = fields.IntField(null=False)
    user = fields.ReferenceField(User)

    client_id = fields.StringField(null=False)
    client = fields.ReferenceField(Client)

    code = fields.StringField(null=False)

    redirect_uri = fields.StringField()
    expires = fields.DateTimeField()

    _scopes = fields.StringField()

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(Document):
    id = fields.SequenceField(primary_key=True)

    user_id = fields.IntField(null=False)
    user = fields.ReferenceField(User)

    client_id = fields.StringField(null=False)
    client = fields.ReferenceField(Client)

    # currently only bearer is supported
    token_type = fields.StringField()

    access_token = fields.StringField(unique=True)
    refresh_token = fields.StringField(unique=True)
    expires = fields.DateTimeField()
    _scopes = fields.StringField()

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []