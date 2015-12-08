"""
controllers.py

Point module controllers.
"""

from flask import Blueprint, request, Response, abort, jsonify
from werkzeug.exceptions import BadRequest
from datetime import datetime
import logging

from app.mod_point.models import Point
from app.mod_auth import oauth
from app.decorators import crossdomain

mod_point = Blueprint('point', __name__, url_prefix='/api/v1/point')


@mod_point.route('/<adventure_slug>/<point_type>', methods=['GET'])
@crossdomain(origin='*')
def list_point(adventure_slug, point_type):
    points = Point.objects(adventure=adventure_slug, type=point_type)
    return Response(points.to_json(), mimetype='application/json')


@mod_point.route('/<point_id>', methods=['GET'])
@crossdomain(origin='*')
def get_point(point_id):
    point = Point.objects.get(id=point_id)
    return jsonify(point.to_mongo())


@mod_point.route('/<point_id>', methods=['PUT'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def update_point(point_id):
    point = Point.objects.get(id=point_id)

    try:
        update = {
            'set__title': request.form.get('title', None),
            'set__latitude': float(request.form.get('latitude', None)),  # TODO: accept none
            'set__longitude': float(request.form.get('longitude', None)),  # TODO: accept none
            'set__desc': request.form.get('desc', None),
            'set__resource': request.form.get('resource', None),
            'set__thumb': request.form.get('thumb', None),
            'set__photo': request.form.get('photo', None),
            'set__video': request.form.get('video', None),
            'set__timestamp': datetime.strptime(request.form.get('timestamp', datetime.now()), "%Y-%m-%dT%H:%M:%S.%fZ"),
            'set__hide': bool(request.form.get('hide', None)),  # TODO: accept none
            'set__delorme_id': int(request.form.get('delorme_id', None))  # TODO: accept none
        }

        point.update(**update)
        return jsonify(point)
    except TypeError:
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
            title=request.form.get('title', None),
            latitude=float(request.form.get('latitude', None)),  # TODO: accept none
            longitude=float(request.form.get('longitude', None)),  # TODO: accept none
            desc=request.form.get('desc', None),
            resource=request.form.get('resource', None),
            timestamp=datetime.strptime(request.form.get('timestamp', None), "%Y-%m-%dT%H:%M:%S.%fZ"),
            thumb=request.form.get('thumb', None),
            photo=request.form.get('photo', None),
            video=request.form.get('video', None),
            hide=bool(request.form.get('hide', None)),  # TODO: accept none
            delorme_id=int(request.form.get('delorme_id', None)),  # TODO: accept none
            type=point_type,
            adventure=adventure_slug
        )
        point.save()
        return jsonify(point)
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


@mod_point.route('/<point_id>', methods=['DELETE'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def delete_point(point_id):
    point = Point.objects.get(id=point_id)
    try:
        point.delete()
        return jsonify(point)
    except TypeError:
        abort(400)
    except BadRequest as e:
        logging.error(e)
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)
    return
