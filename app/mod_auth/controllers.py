"""
controllers.py

Point module controllers.
"""

from flask import Blueprint, request, jsonify, render_template, redirect
from datetime import datetime, timedelta

from werkzeug.security import gen_salt

from app.mod_user.controllers import current_user

from app.mod_auth.models import Client
from app.mod_auth.models import Grant
from app.mod_auth.models import Token

from app.mod_auth import oauth

mod_auth = Blueprint('auth', __name__, url_prefix='')


@mod_auth.route('/client')
def client():
    item = Client(
        client_id=gen_salt(40),
        client_secret=gen_salt(50),
        _redirect_uris=' '.join([
            'http://myadventure.dev:8000/authorized'
        ]),
        _default_scopes='email'
    )
    item.save()
    return jsonify(
        client_id=item.client_id,
        client_secret=item.client_secret,
    )


@oauth.clientgetter
def load_client(client_id):
    return Client.objects(client_id=client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.objects(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=current_user(),
        expires=expires
    )
    grant.save()
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.objects(access_token=access_token).first()
    elif refresh_token:
        return Token.objects(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = Token.objects(
        client_id=request.client.client_id,
        user_id=request.user.get_id()
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
        user_id=request.user.get_id(),
    )
    tok.save()
    return tok


# @oauth.usergetter
# def get_user(username, password, *args, **kwargs):
#     user = User.objects(email=username).first()
#     return user


@mod_auth.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
def authorize(*args, **kwargs):
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.objects(client_id=client_id).first()
        kwargs['client'] = client
        kwargs['user'] = user
        return render_template('authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'


@mod_auth.route('/oauth/token', methods=['GET', 'POST'])
@oauth.token_handler
def access_token():
    return None


@mod_auth.route('/oauth/revoke', methods=['POST'])
@oauth.revoke_handler
def revoke_token():
    pass


@mod_auth.route('/api/me')
@oauth.require_oauth('email')
def me():
    print request.oauth
    user = request.oauth.user
    return jsonify(username=user.email)
