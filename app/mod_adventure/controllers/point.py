"""
Initialize adventure point controller

"""

import logging
from datetime import datetime
from flask import request, abort, jsonify
from werkzeug.exceptions import BadRequest
from app.decorators import ignore_exception
from app.mod_auth.models import Point
from app.mod_auth.controllers import oauth
from app.mod_adventure.models.adventure import Adventure
from app.mod_adventure.controllers import MOD_ADVENTURE
from app.decorators import crossdomain


SFLOAT = ignore_exception(TypeError)(float)
SINT = ignore_exception(TypeError)(int)
SBOOL = ignore_exception(TypeError)(bool)


@MOD_ADVENTURE.route('/<slug>/point/<point_type>', methods=['GET'])
@crossdomain(origin='*')
def list_point(slug, point_type):
    """List adventure points."""
    adventure = Adventure.objects(slug=slug).get()
    points = adventure.points.objects(point_type=point_type)
    points = Point.objects(adventure=slug, point_type=point_type)
    points_dict = []
    for point in points:
        points_dict.append(point.to_dict())
    return jsonify(points=points_dict)


@MOD_ADVENTURE.route('/<slug>/point/<point_type>/<point_id>', methods=['GET'])
@crossdomain(origin='*')
def get_point(slug, point_type, point_id):
    """Get a specifc point by id."""
    adventure = Adventure.objects(slug=slug).get()
    point = adventure.points.objects.get(point_type=point_type, point_id=point_id)
    return jsonify(point.to_dict())


@MOD_ADVENTURE.route('/<slug>/point/<point_type>/<point_id>', methods=['PUT'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def update_point(slug, point_type, point_id):
    """Update specific point by id."""
    adventure = Adventure.objects(slug=slug).get()
    point = adventure.points.objects.get(point_type=point_type, point_id=point_id)

    try:
        update = {
            'set__title': request.values.get('title', None),
            'set__desc': request.values.get('desc', None),
            'set__elevation': request.values.get('elevation', None),
            'set__speed': request.values.get('speed', None),
            'set__direction': request.values.get('direction', None),
            'set__latitude': SFLOAT(request.values.get('latitude', None)),
            'set__longitude': SFLOAT(request.values.get('longitude', None)),
            'set__resource': request.values.get('resource', None),
            'set__point_type': point_type,
            'set__timestamp': datetime.strptime( \
                request.values.get('timestamp', datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z") \
            ), "%Y-%m-%dT%H:%M:%S.%fZ"),
            'set__delorme_id': SINT(request.values.get('delorme_id', None)),
            'set__hide': SBOOL(request.values.get('hide', None)),
            'set__thumb': request.values.get('thumb', None),
            'set__photo': request.values.get('photo', None),
            'set__video': request.values.get('video', None)
        }

        point.update(**update)
        point.reload()
        return jsonify(point.to_dict())
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest as err:
        logging.error(err)
        abort(400)
    return


@MOD_ADVENTURE.route('/<slug>/point/<point_type>', methods=['POST'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def add_point(slug, point_type):
    """Add new point to adventure."""
    try:
        adventure = Adventure.objects(slug=slug).get()
        point = Point(
            title=request.values.get('title', None),
            desc=request.values.get('desc', None),
            elevation=request.values.get('elevation', None),
            speed=request.values.get('speed', None),
            direction=request.values.get('direction', None),
            latitude=SFLOAT(request.values.get('latitude', None)),
            longitude=SFLOAT(request.values.get('longitude', None)),
            resource=request.values.get('resource', None),
            point_type=point_type,
            timestamp=datetime.strptime(request.values.get( \
                'timestamp', datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ") \
            ), "%Y-%m-%dT%H:%M:%S.%fZ"),
            delorme_id=SINT(request.values.get('delorme_id', None)),
            hide=SBOOL(request.values.get('hide', None)),
            thumb=request.values.get('thumb', None),
            photo=request.values.get('photo', None),
            video=request.values.get('video', None),
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


@MOD_ADVENTURE.route('/<slug>/point/<point_type>/<point_id>', methods=['DELETE'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def delete_point(slug, point_type, point_id):
    """Delete specific point by id."""
    adventure = Adventure.objects(slug=slug).get()
    point = adventure.points.objects.get(point_type=point_type, point_id=point_id)
    try:
        point.delete()
        return jsonify(point.to_dict())
    except BadRequest as err:
        logging.error(err)
        abort(400)
    return
