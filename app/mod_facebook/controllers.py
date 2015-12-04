"""
controllers.py

Facebook module controllers.
"""

from flask import Blueprint, url_for, request, current_app, session, Response, redirect
from flask_oauthlib import client
import ConfigParser

from mongoengine import DoesNotExist

from app.mod_user.models import User

config = ConfigParser.ConfigParser()
config.readfp(open('facebook.config'))

mod_facebook = Blueprint('facebook', __name__, url_prefix='/facebook')

oauth = client.OAuth(current_app)

facebook = oauth.remote_app(
    'facebook',
    consumer_key=config.get('facebook', 'APP_ID'),
    consumer_secret=config.get('facebook', 'APP_SECRET'),
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    access_token_method='GET',
    authorize_url='https://www.facebook.com/dialog/oauth'
)


def current_user():
    me = facebook.get('/me?fields=id,name,email,link')
    if me is None:
        return redirect(url_for('login'))
    try:
        user = User.objects.get(facebook_id=me.data.get('id'))
    except DoesNotExist:
        user = User(
            email=me.data.get('email'),
            name=me.data.get('name'),
            facebook_id=me.data.get('id')
        )
        user.save()
    return user


@mod_facebook.route('/login')
def login():
    callback = url_for(
        'facebook.facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return facebook.authorize(callback=callback)


@mod_facebook.route('/login/authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, client.OAuthException):
        return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me?fields=id,name,email,link')
    return Response('Logged in as id=%s name=%s email=%s redirect=%s' % (me.data.get('id'), me.data.get('name'), me.data.get('email'), request.args.get('next')))


@mod_facebook.route('/me')
def me():
    me = facebook.get('/me?fields=id,name,email,link')
    return Response('Logged in as id=%s name=%s email=%s redirect=%s' % (me.data.get('id'), me.data.get('name'), me.data.get('email'), request.args.get('next')))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')



