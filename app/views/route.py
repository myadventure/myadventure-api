"""
Initialize adventure route controller

"""

from datetime import datetime
import json
import logging
import urllib2
from flask import Blueprint, abort, request, Response
from werkzeug.exceptions import BadRequest
from pykml import parser
from app.models.point import Point
from app.mod_auth.controllers import oauth
from app.decorators import crossdomain

MOD_ROUTE = Blueprint('route', __name__, url_prefix='/api/v1/adventure/<slug>/route')

@MOD_ROUTE.route('/load_from_url', methods=['POST'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def load_route():
    """Load route from provided URL."""
    data = json.loads(request.data)
    url = data['url']

    obj = urllib2.urlopen(url)
    res = obj.read()
    kml_str = ""
    for line in iter(res.splitlines()):
        if not 'atom:link' in line:
            kml_str += line
            kml_str += '\n'

    Point.objects(type='route').delete()

    root = parser.fromstring(kml_str)

    pointid = 1000
    for placemark in root.Document.Folder.Placemark:
        coordinates = placemark.MultiGeometry.Point.coordinates.text.split(',')
        try:
            point = Point(
                title=placemark.name.text,
                type='route',
                latitude=float(coordinates[1]),
                longitude=float(coordinates[0]),
                pointid=pointid,
                timestamp=datetime.now()
            )
        except TypeError:
            abort(500)
        try:
            point.save()
        except TypeError:
            abort(400)
        except BadRequest as err:
            logging.error(err)
            abort(400)

        pointid += 1

    return Response(json.dumps({'status': 'ok'}), status=200, mimetype='application/json')
