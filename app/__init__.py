import os
from mongoengine import connect
from flask import Flask, request, session, redirect, render_template
from app.mod_point.controllers import mod_point
from app.mod_route.controllers import mod_route
from app.mod_config.controllers import mod_config
from app.mod_delorme.controllers import mod_delorme
from app.mod_spot.controllers import mod_spot
from app.mod_flickr.controllers import mod_flickr
from app.mod_instagram.controllers import mod_instagram
from app.mod_auth.controllers import mod_auth
from app.mod_auth.models import User
from app.mod_auth.controllers import current_user
from app.mod_auth import oauth

app = Flask(__name__, static_folder=os.getcwd() + '/app/static', static_url_path='', template_folder=os.getcwd() + '/app/templates')

app.config.from_object('config')

connect(
    host=app.config['MONGODB_URI']
)

oauth.init_app(app)


@app.errorhandler(400)
def bad_request(e):
    """Return a custom 400 error."""
    return 'The browser (or proxy) sent a request that this server could not understand.', 400


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def internal_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


@app.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.objects(username=username).first()
        if not user:
            user = User(username=username)
            user.save()
        session['id'] = user.id
        return redirect('/')
    user = current_user()
    return render_template('home.html', user=user)

# Registering module blueprints
app.register_blueprint(mod_point)
app.register_blueprint(mod_route)
app.register_blueprint(mod_config)
app.register_blueprint(mod_delorme)
app.register_blueprint(mod_spot)
app.register_blueprint(mod_flickr)
app.register_blueprint(mod_instagram)
app.register_blueprint(mod_auth)
