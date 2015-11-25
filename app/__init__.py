from mongoengine import connect
from flask import Flask
import logging
import os

app = Flask(__name__, static_folder=os.getcwd() + '/static', static_url_path='', template_folder=os.getcwd() + '/templates')

app.config.from_object('config')

connect(
    host=app.config['MONGODB_URI']
)

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

from app.mod_tracker.controllers import mod_tracker
app.register_blueprint(mod_tracker)
