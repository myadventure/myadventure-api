"""
load_route.py

Load route points from url.
"""

from datetime import datetime
import urllib2
from flask import abort
from pykml import parser


def load_route(url):
    """Load route from provided URL."""

    obj = urllib2.urlopen(url)
    res = obj.read()
    kml_str = ""
    for line in iter(res.splitlines()):
        if not 'atom:link' in line:
            kml_str += line
            kml_str += '\n'

    root = parser.fromstring(kml_str)

    points = []

    for placemark in root.Document.Folder.Placemark:
        coordinates = placemark.MultiGeometry.Point.coordinates.text.split(',')
        try:
            point = {
                'title':placemark.name.text,
                'point_type':'route',
                'latitude':float(coordinates[1]),
                'longitude':float(coordinates[0]),
                'timestamp':datetime.now()
            }
            points.append(point)
        except TypeError:
            abort(500)

    return points
