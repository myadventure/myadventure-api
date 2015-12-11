"""
controllers.py

Point module controllers.
"""
from flask import Blueprint, request, abort, jsonify
from werkzeug.exceptions import BadRequest
from datetime import datetime
import logging

from app.decorators import ignore_exception
from app.mod_point.models import Point
from app.mod_auth import oauth
from app.decorators import crossdomain

mod_point = Blueprint('point', __name__, url_prefix='/api/v1/point')

sfloat = ignore_exception(TypeError)(float)
sint = ignore_exception(TypeError)(int)
sbool = ignore_exception(TypeError)(bool)


@mod_point.route('/<adventure_slug>/<point_type>', methods=['GET'])
@crossdomain(origin='*')
def list_point(adventure_slug, point_type):
    points = Point.objects(adventure=adventure_slug, type=point_type)
    points_dict = []
    for point in points:
        points_dict.append(point.to_dict())
    return jsonify(points=points_dict)


@mod_point.route('/<point_id>', methods=['GET'])
@crossdomain(origin='*')
def get_point(point_id):
    point = Point.objects.get(id=point_id)
    return jsonify(point.to_dict())


@mod_point.route('/<point_id>', methods=['PUT'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def update_point(point_id):
    point = Point.objects.get(id=point_id)

    try:
        update = {
            'set__title': request.values.get('title', None),
            'set__latitude': sfloat(request.values.get('latitude', None)),
            'set__longitude': sfloat(request.values.get('longitude', None)),
            'set__desc': request.values.get('desc', None),
            'set__resource': request.values.get('resource', None),
            'set__thumb': request.values.get('thumb', None),
            'set__photo': request.values.get('photo', None),
            'set__video': request.values.get('video', None),
            'set__timestamp': datetime.strptime(request.values.get('timestamp', datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")), "%Y-%m-%dT%H:%M:%S.%fZ"),
            'set__hide': sbool(request.values.get('hide', None)),
            'set__delorme_id': sint(request.values.get('delorme_id', None))
        }

        point.update(**update)
        point.reload()
        return jsonify(point.to_dict())
    except TypeError as e:
        logging.error(e)
        abort(400)
    except BadRequest as e:
        logging.error(e)
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)
    return


@mod_point.route('/<adventure_slug>/<point_type>', methods=['POST'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def add_point(adventure_slug, point_type):
    try:
        point = Point(
            title=request.values.get('title', None),
            latitude=sfloat(request.values.get('latitude', None)),
            longitude=sfloat(request.values.get('longitude', None)),
            desc=request.values.get('desc', None),
            resource=request.values.get('resource', None),
            timestamp=datetime.strptime(request.values.get('timestamp', datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")), "%Y-%m-%dT%H:%M:%S.%fZ"),
            thumb=request.values.get('thumb', None),
            photo=request.values.get('photo', None),
            video=request.values.get('video', None),
            hide=sbool(request.values.get('hide', None)),
            delorme_id=sint(request.values.get('delorme_id', None)),
            type=point_type,
            adventure=adventure_slug
        )
        point.save()
        return jsonify(point.to_dict())
    except ValueError as e:
        logging.error(e)
        abort(400)
    except BadRequest as e:
        logging.error(e)
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)
    return


@mod_point.route('/<point_id>', methods=['DELETE'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def delete_point(point_id):
    point = Point.objects.get(id=point_id)
    try:
        point.delete()
        return jsonify(point.to_dict())
    except BadRequest as e:
        logging.error(e)
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)
    return
