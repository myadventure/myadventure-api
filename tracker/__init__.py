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

    app.debug = True

    app.secret_key = config.get('tracker', 'secret_key')

    mongodb = config.get('tracker', 'mongodb')

    connect(
        host=mongodb
    )

    views.load_routes(app)

    facebook.load_routes(app)

    app.run(debug=True)
