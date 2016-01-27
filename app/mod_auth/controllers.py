"""
models.py

Auth module controllers.
"""
from flask import Blueprint, request, render_template, abort, redirect, url_for
from flask_login import current_user, login_user, LoginManager, login_required
from flask_oauthlib.provider import OAuth2Provider

from app.mod_user.models import User
from app.mod_auth.forms import LoginForm
from app.mod_auth.models import Client

from validators import RequestValidator

oauth = OAuth2Provider()
oauth._validator = RequestValidator()

mod_auth = Blueprint('auth', __name__, url_prefix='')

login_manager = LoginManager()


def next_is_valid(next):
    return True


@mod_auth.record_once
def on_load(state):
    login_manager.init_app(state.app)
    login_manager.login_view = ".login"


@login_manager.user_loader
def user_loader(id):
    user = User.objects.get(id=id)
    return user


@mod_auth.route('/login', methods=['GET', 'POST'])
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

                if not next_is_valid(next):
                    return abort(401)
                return redirect(next or url_for(".authorize"))
            return abort(401)
        return abort(400)
    return render_template('login.html', form=form)


@mod_auth.route('/oauth/token', methods=['POST'])
@oauth.token_handler
def access_token():
    return None


@mod_auth.route('/oauth/revoke', methods=['POST'])
@oauth.revoke_handler
def revoke_token():
    """ This endpoint allows a user to revoke their access token."""
    pass


@mod_auth.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
@login_required
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.objects.get(client_id=client_id)
        kwargs['client'] = client
        kwargs['user'] = current_user
        return render_template('authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'



