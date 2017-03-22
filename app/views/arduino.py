"""
android.py

Android views.

"""

import logging
from datetime import datetime
from flask import Blueprint, abort, request, jsonify
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
    """Create a new point based on post parameters."""
    try:
        timestamp = datetime.now()
        adventure = Adventure.objects(slug=slug).get()
        point = Point(
            title='Arduino tracker information received.',
            desc=None,
            altitude=request.form.get('alt', None),
            speed=request.form.get('spd', None),
            direction=request.form.get('dir', None),
            latitude=SFLOAT(request.form.get('lat', None)),
            longitude=SFLOAT(request.form.get('lon', None)),
            resource=None,
            point_type='tracker',
            timestamp=timestamp,
            delorme_id=None,
            aio_id=None,
            hide=bool(request.form.get('hide', None) in ['true', 'True', 'TRUE', '1', 'y', 'yes']),
            thumb=None,
            photo=None,
            video=None,
            source='arduino',
            battery=SINT(request.form.get('bat', None)),
            user=None
        )
        adventure.points.append(point)
        adventure.save()
        return jsonify({'status': "ok"})
    except ValueError as err:
        logging.error(err)
        abort(400)
    except BadRequest as err:
        logging.error(err)
        abort(400)
    return jsonify({'status': "ok"})
