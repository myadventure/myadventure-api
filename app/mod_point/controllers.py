"""
controllers.py

Point module controllers.
"""

from flask import Blueprint, request, Response, abort
from werkzeug.exceptions import BadRequest
from datetime import datetime
import json
import bson
import logging

from app.mod_point.models import Point

mod_point = Blueprint('point', __name__, url_prefix='/api/v1/point')


@mod_point.route('/<type>', methods=['GET'])
def list_point(type):
    points_dict = None
    if points_dict is None:
        points_dict = []
        points = Point.objects(Point.type == type).order_by('timestamp', 'pointid')
        for point in points:
            points_dict.append(point.to_dict())

    return Response(bson.json_util.dumps(points_dict), mimetype='application/json');


@mod_point.route('/<type>/<id>', methods=['GET'])
def get_point(type, id):
    point = Point.objects.get(id=id)
    return Response(bson.json_util.dumps(point.to_dict()), mimetype='application/json');


@mod_point.route('/<type>/<id>', methods=['PUT'])
def update_point(type, id):
    point = Point.objects.get(id=id)

    try:
        data = json.loads(request.data)

        if 'title' in data:
            point.title = data['title']

        if 'latitude' in data:
            point.latitude = float(data['latitude'])

        if 'longitude' in data:
            point.longitude = float(data['longitude'])

        if 'desc' in data:
            point.desc = data['desc']

        if 'resource' in data:
            point.resource = data['resource']

        if 'thumb' in data:
            point.thumb = data['thumb']

        if 'photo' in data:
            point.photo = data['photo']

        if 'video' in data:
            point.video = data['video']

        if 'timestamp' in data:
            point.timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")

        if 'hide' in data:
            point.hide = bool(data['hide'])

        point.save()
    except TypeError:
        abort(400)
    except BadRequest as e:
        logging.error(e)
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)

    return Response(bson.json_util.dumps(point.to_dict()), mimetype='application/json');


@mod_point.route('/<type>', methods=['POST'])
def add_point(type):
    try:
        data = json.loads(request.data)

        title = None
        if 'title' in data:
            title = data['title']

        if 'latitude' in data:
            latitude = float(data['latitude'])
        else:
            abort(400)

        if 'longitude' in data:
            longitude = float(data['longitude'])
        else:
            abort(400)

        desc = None
        if 'desc' in data:
            desc = data['desc']

        resource = None
        if 'resource' in data:
            resource = data['resource']

        thumb = None
        if 'thumb' in data:
            thumb = data['thumb']

        photo = None
        if 'photo' in data:
            photo = data['photo']

        video = None
        if 'video' in data:
            video = data['video']

        timestamp = datetime.now()
        if 'timestamp' in data:
            timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")

        point = Point(
            title=title,
            latitude=latitude,
            longitude=longitude,
            desc=desc,
            resource=resource,
            timestamp=timestamp,
            thumb=thumb,
            photo=photo,
            video=video,
            type=type
        )

        point.save()
    except TypeError:
        abort(400)
    except BadRequest as e:
        logging.error(e)
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)

    return Response(bson.json_util.dumps(point.to_dict()), mimetype='application/json');


@mod_point.route('/<type>/<id>', methods=['DELETE'])
def delete_point(type, id):
    point = Point.objects.get(id=id)
    try:
        point.key.delete()
    except TypeError:
        abort(400)
    except BadRequest as e:
        logging.error(e)
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)

    return Response(bson.json_util.dumps({ 'status': 'ok' }), mimetype='application/json')
