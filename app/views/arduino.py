"""
android.py

Android views.

"""

import logging
from datetime import datetime
from flask import Blueprint, abort, request, jsonify
from flask_login import login_required
from werkzeug.exceptions import BadRequest
from app.decorators import crossdomain, ignore_exception
from app.models.adventure import Adventure
from app.models.point import Point

SFLOAT = ignore_exception(TypeError)(float)
SINT = ignore_exception(TypeError)(int)
SBOOL = ignore_exception(TypeError)(bool)


MOD_ARDUINO = Blueprint('arduino', __name__, url_prefix='/api/v1/adventure/<slug>/arduino')

@MOD_ARDUINO.route('/', methods=['POST'])
@crossdomain('*')
def add_point(slug):
    """Create a new point based on get parameters."""
    print request.form.get('lat')
    return jsonify({'status': "ok"})
