from flask import Flask, redirect, url_for, request
from flask_oauthlib.client import OAuth, OAuthException

FACEBOOK_APP_ID = '188477911223606'
FACEBOOK_APP_SECRET = '621413ddea2bcc5b2e83d42fc40495de'

def load_routes(app):

    oauth = OAuth(app)

    facebook = oauth.remote_app(
        'facebook',
        consumer_key=FACEBOOK_APP_ID,
        consumer_secret=FACEBOOK_APP_SECRET,
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
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        if isinstance(resp, OAuthException):
            return 'Access denied: %s' % resp.message

        #TODO: move this crap out of session
        session['oauth_token'] = (resp['access_token'], '')
        me = facebook.get('/me')
        return 'Logged in as id=%s name=%s redirect=%s' % \
            (me.data['id'], me.data['name'], request.args.get('next'))


    @facebook.tokengetter
    def get_facebook_oauth_token():
        #TODO: move this crap out of session
        return session.get('oauth_token')
