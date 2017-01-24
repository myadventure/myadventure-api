"""
controllers.py

Delorme module controllers.
"""
import json
import urllib2
import logging
from datetime import datetime
import bson
from pykml import parser
from flask import Response, Blueprint, request, jsonify, abort
from werkzeug.exceptions import BadRequest
from app.mod_adventure.models import Adventure
from app.mod_point.models import Point
from app.mod_delorme.models import Delorme
from app.decorators import crossdomain
from app.mod_auth.controllers import oauth

MOD_DELORME = Blueprint('delorme', __name__, url_prefix='/api/v1/delorme')


def load_data(url):
    """Load DeLorme inReach data from specified feed URL."""
    obj = urllib2.urlopen(url)
    root = parser.parse(obj).getroot()
    for placemark in root.Document.Folder.Placemark:
        try:
            point = None
            extended_data = placemark.ExtendedData.Data
            delorme_id = None
            event = None
            elevation = None
            velocity = None
            course = None
            text = None
            point_type = 'tracker'
            for data in extended_data:
                if data.attrib['name'] == 'Id':
                    delorme_id = int(data.value.text)
                elif data.attrib['name'] == 'Event':
                    event = data.value.text.encode('utf-8')
                elif data.attrib['name'] == 'Elevation':
                    elevation = data.value.text.encode('utf-8')
                elif data.attrib['name'] == 'Velocity':
                    velocity = data.value.text.encode('utf-8')
                elif data.attrib['name'] == 'Course':
                    course = data.value.text.encode('utf-8')
                elif data.attrib['name'] == 'Text':
                    text = data.value.text
                    if text is not None:
                        text = text.encode('utf-8')
            if delorme_id is not None:
                point = Point.objects(delorme_id == delorme_id).first()
            if point is None:
                title = event
                coordinates = placemark.Point.coordinates.text.split(',')
                latitude = float(coordinates[1])
                longitude = float(coordinates[0])
                timestamp = datetime.strptime(placemark.TimeStamp.when.text, "%Y-%m-%dT%H:%M:%SZ")

                if text is not None:
                    desc = text
                    point_type = 'message'
                else:
                    desc = ''
                    if elevation is not None:
                        desc = desc + "Elevation: {elevation}<br>".format(elevation=elevation)
                    if velocity is not None:
                        desc = desc + "Velocity: {velocity}<br>".format(velocity=velocity)
                    if course is not None:
                        desc = desc + "Course: {course}<br>".format(course=course)

                point = Point(
                    title=title,
                    latitude=latitude,
                    longitude=longitude,
                    point_type=point_type,
                    timestamp=timestamp,
                    delorme_id=delorme_id,
                    desc=desc
                )
                point.save()
        except AttributeError:
            pass

    return Response(json.dumps({'status': 'ok'}), status=200, mimetype='application/json')


@MOD_DELORME.route('/<adventure_slug>/load', methods=['GET'])
@oauth.require_oauth('email')
def load_tracker(adventure_slug):
    """Load DeLorme inReach tracker points from configured feed URL."""
    adventure = Adventure.objects().get(slug=adventure_slug)
    delorme = adventure.delorme
    if delorme is not None:
        return load_data(delorme.url)
    return Response(bson.json_util.dumps( \
        {'error': 'DeLorme tracker URL is not configured.'} \
    ), status=500, mimetype='application/json')


@MOD_DELORME.route('/<adventure_slug>', methods=['POST'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def add_tracker(adventure_slug):
    """Add tracker feed URL to Adventure object defined by adventure_slug"""
    try:
        adventure = Adventure.objects.get(slug=adventure_slug)
        url = request.values.get('url', None)
        delorme = Delorme(
            url=url
        )
        adventure.delorme = delorme
        adventure.save()

        return jsonify(adventure.to_mongo())
    except TypeError as e:
        logging.error(e)
        abort(400)
    except BadRequest:
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)
    return

