from flask import Flask, redirect, url_for, request
from flask_oauthlib.client import OAuth, OAuthException
import bson

def load_routes(app):

    oauth = OAuth(app)

    facebook = oauth.remote_app(
        'facebook',
        consumer_key=app.facebook_app_id,
        consumer_secret=app.facebook_app_secret,
        request_token_params={'scope': 'email'},
        base_url='https://graph.facebook.com',
        request_token_url=None,
        access_token_url='/oauth/access_token',
        access_token_method='GET',
        authorize_url='https://www.facebook.com/dialog/oauth'
    )

    @app.route('/login')
    def login():
        callback = url_for(
            'facebook_authorized',
            next=request.args.get('next') or request.referrer or None,
            _external=True
        )
        return facebook.authorize(callback=callback)


    @app.route('/login/authorized')
    def facebook_authorized():
        resp = facebook.authorized_response()
        if resp is None:

            return bson.json_util.dumps({
                'error': 'Access denied',
                'reason': request.args['error_reason'],
                'description': request.args['error_description']
            })

        if isinstance(resp, OAuthException):
            return 'Access denied: %s' % resp.message

        me = facebook.get('/me')

        return  bson.json_util.dumps({
            'id': me.data['id'],
            'name': me.data['name'],
            'redirect': request.args.get('next'),
            'access_token': resp['access_token']
        })


    @facebook.tokengetter
    def get_facebook_oauth_token():
        token = request.args.get('token', '')
        return (token, '')
