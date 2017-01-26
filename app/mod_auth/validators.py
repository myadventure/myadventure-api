"""
validators.py

Auth module validators
"""
import logging
import re
from datetime import datetime, timedelta

from flask_login import current_user
from flask_oauthlib.provider import OAuth2RequestValidator
from flask_oauthlib.utils import decode_base64
from mongoengine import DoesNotExist
from oauthlib.common import to_unicode

from app.models.user import User
from app.models.facebook import Facebook
from models import Client, Grant, Token


def load_client(client_id):
    try:
        return Client.objects.get(client_id=client_id)
    except DoesNotExist:
        logging.info("Client not found.")
        return None


def load_user(username, password, client, request, *args, **kwargs):
    if re.match(r"[^@]+@[^@]+\.[^@]+", username):
        if not client.has_password_credential_permission:
            return None
        try:
            user = User.objects.get(email=username)
        except DoesNotExist:
            logging.info("User not found.")
            return None
        if not user.validate_password(password):
            return None

        return user
    elif username.isdigit():
        if not client.has_facebook_credential_permission:
            return None

        try:
            facebook = Facebook(password)
            me = facebook.get('/me', params={'fields': 'id,name,email,link'})
        except client.OAuthException:
            return None
        except Exception as e:
            logging.error(e)
            return None

        try:
            user = User.objects.get(facebook_id=username)
            user.facebook_access_token = password
            user.save()
        except DoesNotExist:
            facebook_id = me['id']
            email = me['email']
            name = me['name']
            user = User(
                facebook_id=facebook_id,
                email=email,
                name=name,
                facebook_access_token=password,
                password=None,
                salt=None,
            )
            user.save()

        return user
    else:
        logging.warning("Username not recognized.")
        return None


def load_grant(client_id, code, *args, **kwargs):
    return Grant.objects.get(client_id=client_id, code=code)


def save_grant(client_id, code, request, *args, **kwargs):
    expires = datetime.utcnow() + timedelta(seconds=3600)
    user = User.objects.get(user_id=current_user.user_id)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=user,
        user_id=user.user_id,
        expires=expires
    )
    grant.save()
    return grant


def load_token(access_token=None, refresh_token=None):
    if access_token:
        try:
            return Token.objects.get(access_token=access_token)
        except DoesNotExist:
            logging.info("Access token not found.")
    elif refresh_token:
        try:
            return Token.objects.get(refresh_token=refresh_token)
        except DoesNotExist:
            logging.info("Refresh token not found.")
    return None


def save_token(token, request, *args, **kwargs):
    user = request.user
    toks = Token.objects(
        client_id=request.client.client_id,
        user_id=user.user_id
    )
    # make sure that every client has only one token connected to a user
    for t in toks:
        t.delete()

    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=user.user_id,
        user=user
    )
    tok.save()
    return tok


class RequestValidator(OAuth2RequestValidator):
    def __init__(self):
        self._usergetter = load_user
        self._clientgetter = load_client
        self._tokengetter = load_token
        self._tokensetter = save_token
        self._grantgetter = load_grant
        self._grantsetter = save_grant

    def authenticate_client(self, request, *args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if auth:
            try:
                _, s = auth.split(' ')
                client_id, client_secret = decode_base64(s).split(':')
                client_id = to_unicode(client_id, 'utf-8')
            except Exception as e:
                logging.info('Authenticate client failed with exception: %r', e)
                return False
        else:
            client_id = request.client_id

        client = self._clientgetter(client_id)
        if not client:
            logging.info('Authenticate client failed, client not found.')
            return False

        if client.client_type == 'public':
            return self.authenticate_client_id(client_id, request)
        else:
            return OAuth2RequestValidator.authenticate_client(
                self, request, *args, **kwargs)
