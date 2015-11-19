"""
Initialize Flask app

"""

from flask import Flask
import logging
import os
import ConfigParser

config = ConfigParser.ConfigParser()
config.read(os.getcwd() + '/app.config')

app = Flask(__name__, static_folder=os.getcwd() + '/static', static_url_path='', template_folder=os.getcwd() + '/templates')

app.secret_key = config.get('Tracker', 'secret_key')

import views
