"""
Initialize adventure point controller

"""

import logging
from datetime import datetime
from flask import Blueprint, request, abort, jsonify
from werkzeug.exceptions import BadRequest
from mongoengine.queryset.visitor import Q
from app.decorators import ignore_exception
from app.views.auth import OAUTH
from app.models.adventure import Adventure
from app.models.point import Point
from app.decorators import crossdomain


MOD_POINT = Blueprint( \
    'point', __name__, url_prefix='/api/v1/adventure/<slug>/point/<point_type>' \
)

SFLOAT = ignore_exception(TypeError)(float)
SINT = ignore_exception(TypeError)(int)
SBOOL = ignore_exception(TypeError)(bool)


@MOD_POINT.route('/', methods=['GET'])
@crossdomain(origin='*')
def list_point(slug, point_type):
    """List adventure points."""
    points = Adventure.objects.get(slug=slug).points.filter(point_type=point_type)
    points_dict = []
    for point in points:
        points_dict.append(point.to_dict())
    return jsonify(points=points_dict)


@MOD_POINT.route('/<point_id>', methods=['GET'])
@crossdomain(origin='*')
def get_point(slug, point_type, point_id):
    """Get a specifc point by id."""
    points = Adventure.objects.get(slug=slug).points \
        .filter(point_type=point_type, point_id=point_id)
    points_dict = []
    for point in points:
        points_dict.append(point.to_dict())
    return jsonify(points=points_dict)


@MOD_POINT.route('/<point_id>', methods=['PUT'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def update_point(slug, point_type, point_id):
    """Update specific point by id."""
    timestamp = None
    str_timestamp = request.values.get('timestamp', None)
    if str_timestamp:
        timestamp = datetime.strptime(str_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        timestamp = datetime.now()
    try:
        update = {
            'set__points__S__title': request.values.get('title', None),
            'set__points__S__desc': request.values.get('desc', None),
            'set__points__S__altitude': request.values.get('altitude', None),
            'set__points__S__speed': request.values.get('speed', None),
            'set__points__S__direction': request.values.get('direction', None),
            'set__points__S__latitude': SFLOAT(request.values.get('latitude', None)),
            'set__points__S__longitude': SFLOAT(request.values.get('longitude', None)),
            'set__points__S__resource': request.values.get('resource', None),
            'set__points__S__point_type': point_type,
            'set__points__S__timestamp': timestamp,
            'set__points__S__delorme_id': SINT(request.values.get('delorme_id', None)),
            'set__points__S__aio_id': SINT(request.values.get('aio_id', None)),
            'set__points__S__instagram_id': request.values.get('instagram_id', None),
            'set__points__S__hide': SBOOL(request.values.get('hide', None)),
            'set__points__S__thumb': request.values.get('thumb', None),
            'set__points__S__photo': request.values.get('photo', None),
            'set__points__S__video': request.values.get('video', None),
            'set__points__S__battery': SFLOAT(request.values.get('battery', None)),
            'set__points__S__source': request.values.get('source', None)
        }

        updated_items = Adventure.objects(
            # TODO: Complex query is not working as expected.
            # Updating the first point of the adventure instead of the correct one.
            # Q(slug=slug) & Q(points__point_type=point_type) & Q(points__point_id=point_id) \
            Q(points__point_id=point_id) \
        ).update(**update)
        if updated_items < 1:
            return jsonify(error='point not found.'), 400
        return jsonify(status='ok')
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest as err:
        logging.error(err)
        abort(400)
    return


@MOD_POINT.route('/', methods=['POST'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def add_point(slug, point_type):
    """Add new point to adventure."""
    timestamp = None
    str_timestamp = request.values.get('timestamp', None)
    if str_timestamp:
        timestamp = datetime.strptime(str_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        timestamp = datetime.now()
    try:
        adventure = Adventure.objects(slug=slug).get()
        point = Point(
            title=request.values.get('title', None),
            desc=request.values.get('desc', None),
            altitude=request.values.get('altitude', None),
            speed=request.values.get('speed', None),
            direction=request.values.get('direction', None),
            latitude=SFLOAT(request.values.get('latitude', None)),
            longitude=SFLOAT(request.values.get('longitude', None)),
            resource=request.values.get('resource', None),
            point_type=point_type,
            timestamp=timestamp,
            delorme_id=SINT(request.values.get('delorme_id', None)),
            aio_id=SINT(request.values.get('aio_id', None)),
            instagram_id=request.values.get('instagram_id', None),
            hide=SBOOL(request.values.get('hide', None)),
            thumb=request.values.get('thumb', None),
            photo=request.values.get('photo', None),
            video=request.values.get('video', None),
            source=request.values.get('source', None),
            battery=SFLOAT(request.values.get('battery', None)),
            user=request.oauth.user
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


@MOD_POINT.route('/<point_id>', methods=['DELETE'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def delete_point(slug, point_type, point_id):
    """Delete specific point by id."""
    try:
        point = Adventure.objects.get(slug=slug).points \
            .filter(point_type=point_type, point_id=point_id).first()
        if point:
            Adventure.objects(slug=slug).update(pull__points=point)
            return jsonify(status='ok')
        return jsonify(error='point not found.'), 400
    except BadRequest as err:
        logging.error(err)
        abort(500)
    return
