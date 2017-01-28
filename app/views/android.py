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


MOD_ANDROID = Blueprint('android', __name__, url_prefix='/api/v1/adventure/<slug>/android')

@MOD_ANDROID.route('/', methods=['GET'])
@login_required
@crossdomain('*')
def add_point(slug):
    """Create a new point based on get parameters."""
    try:
        timestamp = None
        str_timestamp = request.args.get('time', None)
        if str_timestamp:
            timestamp = datetime.strptime(str_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            timestamp = datetime.now()
        adventure = Adventure.objects(slug=slug).get()
        point = Point(
            title='Android tracker information received.',
            desc=request.args.get('desc', None),
            elevation=request.args.get('alt', None),
            speed=request.args.get('spd', None),
            direction=request.args.get('dir', None),
            latitude=SFLOAT(request.args.get('lat', None)),
            longitude=SFLOAT(request.args.get('lon', None)),
            resource=None,
            point_type='tracker',
            timestamp=timestamp,
            delorme_id=None,
            aio_id=None,
            hide=SBOOL(request.args.get('hide', None)),
            thumb=None,
            photo=None,
            video=None,
        )
        adventure.points.append(point)
        adventure.save()
        return jsonify(point.to_dict())
    except ValueError as err:
        logging.error(err)
        abort(400)
    except BadRequest as err:
        logging.error(err)
        abort(400)
    return
