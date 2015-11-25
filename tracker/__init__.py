"""
Initialize Flask app

"""

from flask import Flask
import logging
import os
import ConfigParser
from mongoengine import connect
import views
import facebook

def init():

    config = ConfigParser.ConfigParser()
    config.read(os.getcwd() + '/app.config')

    app = Flask(__name__, static_folder=os.getcwd() + '/static', static_url_path='', template_folder=os.getcwd() + '/templates')

    app.secret_key = config.get('tracker', 'secret_key')

    app.facebook_app_id = config.get('facebook', 'app_id')
    app.facebook_app_secret = config.get('facebook', 'app_secret')

    mongodb = config.get('tracker', 'mongodb')
    host = config.get('tracker', 'host')

    connect(
        host=mongodb
    )

    views.load_routes(app)

    facebook.load_routes(app)

    app.run(debug=True, host=host)
