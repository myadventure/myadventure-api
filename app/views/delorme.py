"""
Initialize adventure delorme controller

"""

import logging
import urllib2
import datetime
from pykml import parser
from flask import Blueprint, abort, request, jsonify
from werkzeug.exceptions import BadRequest
from app.decorators import crossdomain
from app.views.auth import OAUTH
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
            desc = None
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
                point = adventure.points.filter( \
                    point_type=point_type, delorme_id=delorme_id \
                ).first()
            if point is None:
                title = event
                coordinates = placemark.Point.coordinates.text.split(',')
                latitude = float(coordinates[1])
                longitude = float(coordinates[0])
                timestamp = datetime.datetime.strptime( \
                    placemark.TimeStamp.when.text, "%Y-%m-%dT%H:%M:%SZ" \
                )

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
                    aio_id=None,
                    hide=False,
                    thumb=None,
                    photo=None,
                    video=None
                )

                adventure.points.append(point)
                adventure.save()
        except AttributeError as err:
            if 'no such child' not in err.message:
                logging.error(err)
                return abort(500)

    return jsonify({'status': 'ok'})


@MOD_DELORME.route('/', methods=['POST'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def add_delorme(slug):
    """Add Delorme inReach feed URL to Adventure object defined by slug"""
    try:
        adventure = Adventure.objects.get(slug=slug)
        feed_url = request.values.get('feed_url', None)
        adventure.delorme = Delorme(
            feed_url=feed_url
        )
        adventure.save()

        return jsonify({'delorme': adventure.delorme.to_dict()})
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest:
        abort(400)
    return


@MOD_DELORME.route('/', methods=['GET'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def get_delorme(slug):
    """Get Delorme inReach information."""
    try:
        adventure = Adventure.objects.get(slug=slug)
        if adventure.delorme:
            return jsonify({'delorme': adventure.delorme.to_dict()})
        return jsonify({'error': 'DeLorme inReach information is not configured.'}), 400
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest:
        abort(400)
    return


@MOD_DELORME.route('/', methods=['DELETE'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def delete_point(slug):
    """Delete DeLorme inReach information."""
    Adventure.objects(slug=slug).update(unset__delorme=1, upsert=True)
    return jsonify({'status': 'ok'})


@MOD_DELORME.route('/load', methods=['GET'])
@OAUTH.require_oauth('email')
def load_tracker(slug):
    """Load DeLorme inReach tracker points from configured feed URL."""
    adventure = Adventure.objects(slug=slug).get()
    delorme = adventure.delorme
    if delorme.feed_url is not None:
        return load_data(delorme.feed_url, adventure)
    return jsonify({'error': 'DeLorme inReach information is not set.'}), 400
