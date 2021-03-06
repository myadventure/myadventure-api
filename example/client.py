from flask import Flask, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth, OAuthException

CLIENT_ID = '1EssHrEXtGdmJHFQ2YEU1leNsHljVPZp1RmRsYDZ'
CLIENT_SECRET = 'WtAikOHT38puo0FHhNrqYbCi6shLFSJjsmc2KVsms8i7utni1h'


app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'
oauth = OAuth(app)

remote = oauth.remote_app(
    'remote',
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    request_token_params={'scope': 'email'},
    base_url='http://api.myadventure.dev:5000/api/',
    request_token_url=None,
    access_token_url='http://api.myadventure.dev:5000/oauth/token',
    authorize_url='http://api.myadventure.dev:5000/oauth/authorize',
    access_token_method='POST'
)


@app.route('/')
def index():
    if 'remote_oauth' in session:
        resp = remote.get('/api/v1/user')
        if resp.status != 401:
            return jsonify(resp.data)
    next_url = request.args.get('next') or request.referrer or None
    return remote.authorize(
        callback=url_for('authorized', next=next_url, _external=True)
    )


@app.route('/authorized')
def authorized():
    resp = remote.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message
    session['remote_oauth'] = (resp['access_token'], '')
    return jsonify(oauth_token=resp['access_token'])


@remote.tokengetter
def get_oauth_token():
    return session.get('remote_oauth')


if __name__ == '__main__':
    import os
    os.environ['DEBUG'] = 'true'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
    app.run(host='myadventure.dev', port=8000)
