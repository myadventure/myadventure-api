"""
models.py

Auth module MongoEngine models
"""

from mongoengine import Document
from mongoengine import fields
from werkzeug.security import gen_salt

from app.mod_user.models import User


class Client(Document):
    user_id = fields.IntField(null=False)
    user = fields.ReferenceField(User)

    client_id = fields.StringField(primary_key=True)
    client_secret = fields.StringField(null=False)

    is_confidential = fields.BooleanField()

    _redirect_uris = fields.StringField()
    _default_scopes = fields.StringField()

    @property
    def allowed_grant_types(self):
        """ Returns allowed grant types."""
        return ['password', 'authorization_code']

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

    @property
    def has_password_credential_permission(self):
        return True

    @property
    def has_facebook_credential_permission(self):
        return True

    @staticmethod
    def generate(redirect_uris):

        item = Client(
            client_id=gen_salt(40),
            client_secret=gen_salt(50),
            _redirect_uris=' '.join(redirect_uris),
            _default_scopes='email',
            user_id=None,
        )
        item.save()


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