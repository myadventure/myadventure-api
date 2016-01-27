"""
controllers.py

Delorme module controllers.
"""
from flask import Response, Blueprint
import json
import urllib2
from pykml import parser
import logging
from datetime import datetime
import bson

from app.mod_adventure.models import Adventure
from app.mod_point.models import Point

from app.mod_auth.controllers import oauth

mod_delorme = Blueprint('delorme', __name__, url_prefix='/api/v1/delorme')


def load_data(url):
    obj = urllib2.urlopen(url)
    root = parser.parse(obj).getroot()
    for placemark in root.Document.Folder.Placemark:
        try:
            point = None
            extended_data = placemark.ExtendedData.Data
            pointid = None
            event = None
            elevation = None
            velocity = None
            course = None
            text = None
            type='tracker'
            for data in extended_data:
                if data.attrib['name'] == 'Id':
                    pointid = int(data.value.text)
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
            if pointid is not None:
                point = Point.objects(pointid == pointid).first()
            if point is None:
                title = event
                coordinates = placemark.Point.coordinates.text.split(',')
                latitude = float(coordinates[1])
                longitude = float(coordinates[0])
                timestamp = datetime.strptime(placemark.TimeStamp.when.text, "%Y-%m-%dT%H:%M:%SZ")

                if text is not None:
                    desc = text
                    type = 'message'
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
                    type=type,
                    timestamp=timestamp,
                    pointid=pointid,
                    desc=desc
                )
                point.save()
        except AttributeError:
            pass
        except Exception as e:
            logging.error(e.args[0])

    return Response(json.dumps({'status': 'ok'}), status=200, mimetype='application/json')


@mod_delorme.route('/load/<adventure_slug>', methods=['GET'])
@oauth.require_oauth('email')
def load_tracker(adventure_slug):
    adventure = Adventure.objects().get(slug=adventure_slug)
    delorme = adventure.delorme
    if delorme is not None:
        return load_data(delorme.url)
    return Response(bson.json_util.dumps({'error': 'DeLorme tracker URL is not configured.'}), status=500, mimetype='application/json')

