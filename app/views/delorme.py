"""
Initialize adventure delorme controller

"""

import logging
import json
import urllib2
import datetime
from pykml import parser
from flask import Blueprint, abort, request, Response
from werkzeug.exceptions import BadRequest
from app.decorators import crossdomain
from app.mod_auth.controllers import oauth
from app.models.adventure import Adventure
from app.models.delorme import Delorme
from app.models.point import Point

MOD_DELORME = Blueprint('delorme', __name__, url_prefix='/api/v1/adventure/<slug>/delorme')


def load_data(feed_url, adventure):
    """Load DeLorme inReach data from specified feed URL."""
    obj = urllib2.urlopen(feed_url)
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
                point = adventure.objects(delorme_id=delorme_id).first()
            if point is None:
                title = event
                coordinates = placemark.Point.coordinates.text.split(',')
                latitude = float(coordinates[1])
                longitude = float(coordinates[0])
                timestamp = datetime.strptime(placemark.TimeStamp.when.text, "%Y-%m-%dT%H:%M:%SZ")

                if text is not None:
                    desc = text
                    point_type = 'message'

                point = Point(
                    title=title,
                    desc=desc,
                    elevation=elevation,
                    speed=velocity,
                    direction=course,
                    latitude=latitude,
                    longitude=longitude,
                    resource=None,
                    point_type=point_type,
                    timestamp=timestamp,
                    delorme_id=delorme_id,
                    hide=False,
                    thumb=None,
                    photo=None,
                    video=None
                )

                adventure.points.append(point)
                adventure.save()
        except AttributeError:
            pass

    return Response(json.dumps({'status': 'ok'}), status=200, mimetype='application/json')


@MOD_DELORME.route('/', methods=['POST'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def add_delorme(slug):
    """Add Delorme inReach feed URL to Adventure object defined by slug"""
    try:
        adventure = Adventure.objects.get(slug=slug)
        feed_url = request.values.get('feed_url', None)
        adventure.delorme = Delorme(
            feeed_url=feed_url
        )
        adventure.save()

        return Response(json.dumps({'status': 'ok'}), status=200, mimetype='application/json')
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest:
        abort(400)
    return


@MOD_DELORME.route('/load', methods=['GET'])
@oauth.require_oauth('email')
def load_tracker(slug):
    """Load DeLorme inReach tracker points from configured feed URL."""
    adventure = Adventure.objects().get(slug=slug)
    delorme = adventure.delorme
    if delorme.feed_url is not None:
        return load_data(delorme.feed_url, adventure)
    return Response(json.dumps( \
        {'error': 'DeLorme inReach Feed URL not found.'} \
    ), status=500, mimetype='application/json')
