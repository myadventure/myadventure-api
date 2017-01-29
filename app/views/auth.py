"""
auth.py

Auth module controllers.
"""
import urllib
import base64
from flask import Blueprint, request, render_template, abort, redirect, url_for, jsonify
from flask_login import current_user, login_user, LoginManager, login_required, logout_user
from flask_oauthlib.provider import OAuth2Provider
from app.forms import LoginForm
from app.models.user import User
from app.models.auth import Client
from app.validators import RequestValidator

OAUTH = OAuth2Provider()
OAUTH._validator = RequestValidator()

MOD_AUTH = Blueprint('auth', __name__, url_prefix='')

LOGIN_MANAGER = LoginManager()

def next_is_valid(next):
    return True


def validate_api_key(api_key):
    try:
        api_key = base64.b64decode(api_key)
        user_id, password = api_key.strip().split(':')
        user = User.objects(user_id=user_id).get()
        if user:
            if user.validate_password(password):
                return user
    except TypeError:
        pass

    return None


@MOD_AUTH.record_once
def on_load(state):
    LOGIN_MANAGER.init_app(state.app)


@LOGIN_MANAGER.user_loader
def user_loader(user_id):
    user = User.objects.get(user_id=user_id)
    return user


@LOGIN_MANAGER.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        api_key = api_key.encode('ascii')
        return validate_api_key(api_key)

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.encode('ascii')
        api_key = api_key.replace('Basic ', '', 1)
        return validate_api_key(api_key)

    # finally, return None if both methods did not login the user
    return None


@MOD_AUTH.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = request.form.get('email')
            password = request.form.get('password')

            user = User.objects.get(email=email)

            if user.validate_password(password):
                login_user(user)

                next = request.args.get('next')

                if next:
                    params = dict((key, request.args.get(key)) for key in request.args.keys())
                    del params['next']
                    next = next + '?' + urllib.urlencode(params)

                if not next_is_valid(next):
                    return abort(401)

                return redirect(next or jsonify({"status": "ok"}))
            return abort(401)
        return abort(400)
    return render_template('login.html', form=form, values=request.args)


@MOD_AUTH.route("/logout")
@login_required
def logout():
    logout_user()
    next = request.args.get('next')
    return redirect(next or jsonify({"status": "ok"}))


@MOD_AUTH.route('/oauth/token', methods=['POST'])
@OAUTH.token_handler
def access_token():
    return None


@MOD_AUTH.route('/oauth/revoke', methods=['POST'])
@OAUTH.revoke_handler
def revoke_token():
    """ This endpoint allows a user to revoke their access token."""
    pass


@MOD_AUTH.route('/oauth/authorize', methods=['GET', 'POST'])
@OAUTH.authorize_handler
def authorize(*args, **kwargs):
    if current_user.is_anonymous:
        values = kwargs
        del values['request']
        del values['state']
        values['next'] = url_for('.authorize')
        return redirect(url_for('.login', **values))
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.objects.get(client_id=client_id)
        kwargs['client'] = client
        kwargs['user'] = current_user
        return render_template('authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'
