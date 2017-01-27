"""
auth.py

Auth mongoengine models.
"""

from mongoengine import Document
from mongoengine import fields
from werkzeug.security import gen_salt

from app.models.user import User


class Client(Document):
    """Auth Client model."""
    user_id = fields.IntField(null=False)
    user = fields.ReferenceField(User)

    client_id = fields.StringField(primary_key=True)
    client_secret = fields.StringField(null=False)

    is_confidential = fields.BooleanField()

    _redirect_uris = fields.StringField()
    _default_scopes = fields.StringField()

    @property
    def allowed_grant_types(self):
        """Returns allowed grant types."""
        return ['password', 'authorization_code']

    @property
    def client_type(self):
        """Returns client type."""
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        """Returns a list of redirect URIs."""
        if self._redirect_uris:
            return str(self._redirect_uris).split()
        return []

    @property
    def default_redirect_uri(self):
        """Returns the default redirect URI."""
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        """Returns the client scopes."""
        if self._default_scopes:
            return str(self._default_scopes).split()
        return []

    @property
    def has_password_credential_permission(self):
        """Returns true if the client has password permission."""
        return True

    @property
    def has_facebook_credential_permission(self):
        """Returns true if the client has facebook permission."""
        return True

    @staticmethod
    def generate(redirect_uris):
        """Generates a new client."""
        item = Client(
            client_id=gen_salt(40),
            client_secret=gen_salt(50),
            _redirect_uris=' '.join(redirect_uris),
            _default_scopes='email',
            user_id=None,
        )
        item.save()


class Grant(Document):
    """Auth Grant model."""
    grant_id = fields.SequenceField(primary_key=True)

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
        """Returns the grant scopes."""
        if self._scopes:
            return str(self._scopes).split()
        return []


class Token(Document):
    """Client token model."""
    token_id = fields.SequenceField(primary_key=True)

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
        """Returns the token scopes."""
        if self._scopes:
            return str(self._scopes).split()
        return []
