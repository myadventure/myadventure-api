"""
Initialize adventure delorme controller

"""

import logging
import json
import urllib2
import datetime
from pykml import parser
from flask import abort, request, Response
from werkzeug.exceptions import BadRequest
from app.decorators import crossdomain
from app.mod_auth.controllers import oauth
from app.mod_adventure.models.adventure import Adventure
from app.mod_adventure.models.delorme import Delorme
from app.mod_adventure.models.point import Point
from app.mod_adventure.controllers import MOD_ADVENTURE


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
                point = Point.objects(delorme_id=delorme_id).first()
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


@MOD_ADVENTURE.route('/<slug>/delorme', methods=['POST'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def add_delorme(slug):
    """Add Delorme inReach feed URL to Adventure object defined by slug"""
    try:
        adventure = Adventure.objects.get(slug=slug)
        feed_url = request.values.get('feed_url', None)
        delorme = Delorme(
            feeed_url=feed_url
        )
        adventure.delorme = delorme
        adventure.save()

        return Response(json.dumps({'status': 'ok'}), status=200, mimetype='application/json')
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest:
        abort(400)
    return


@MOD_ADVENTURE.route('/<slug>/delorme/load', methods=['GET'])
@oauth.require_oauth('email')
def load_tracker(slug):
    """Load DeLorme inReach tracker points from configured feed URL."""
    adventure = Adventure.objects().get(slug=slug)
    delorme = adventure.delorme
    if delorme is not None:
        return load_data(delorme.url)
    return Response(json.dumps({'status': 'ok'}), status=500, mimetype='application/json')
