"""
adafruit.py

Adafruit.io views

"""

import logging
import json
import urllib2
from datetime import datetime
from flask import Blueprint, abort, request, jsonify
from werkzeug.exceptions import BadRequest
from app.decorators import crossdomain
from app.views.auth import OAUTH
from app.models.adventure import Adventure
from app.models.adafruit import Adafruit
from app.models.point import Point

AIO_URL = 'https://io.adafruit.com'

MOD_ADAFRUIT = Blueprint('adafruit', __name__, url_prefix='/api/v1/adventure/<slug>/adafruit')


def load_data(base_url, username, feed, aio_key, adventure):
    """Load Adafruit.io data."""
    request_headers = {
        "X-AIO-Key": aio_key
    }

    req = urllib2.Request(AIO_URL + base_url + '/' + username + '/feeds/' + feed + '/data', \
        headers=request_headers \
    )

    res = urllib2.urlopen(req)

    data = json.load(res)

    for point in data:
        aio_id = point[u'id']
        timestamp = datetime.strptime(point[u'created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        location = point[u'location']
        latitude = float(location[u'geometry'][u'coordinates'][0])
        longitude = float(location[u'geometry'][u'coordinates'][1])
        altitude = str(location[u'geometry'][u'coordinates'][2])
        speed = str(point[u'value'])



        if aio_id is not None:
            point = adventure.points.filter( \
                    point_type='tracker', aio_id=aio_id \
                ).first()
        if point is None:
            point = Point(
                title='MQTT tracker information received.',
                desc=None,
                elevation=altitude,
                speed=speed,
                direction=None,
                latitude=latitude,
                longitude=longitude,
                resource=None,
                point_type='tracker',
                timestamp=timestamp,
                delorme_id=None,
                aio_id=aio_id,
                hide=False,
                thumb=None,
                photo=None,
                video=None
            )

            adventure.points.append(point)
            adventure.save()

    return jsonify({'status': 'ok'})


@MOD_ADAFRUIT.route('/', methods=['POST'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def add_adafruit(slug):
    """Add Adafruit.io configuration to Adventure object defined by slug."""
    try:
        adventure = Adventure.objects.get(slug=slug)
        base_url = request.values.get('base_url', None)
        username = request.values.get('username', None)
        feed = request.values.get('feed', None)
        aio_key = request.values.get('aio_key', None)

        adventure.adafruit = Adafruit(
            base_url=base_url,
            username=username,
            feed=feed,
            aio_key=aio_key
        )
        adventure.save()

        return jsonify({'status': 'ok'})
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest:
        abort(400)
    return


@MOD_ADAFRUIT.route('/', methods=['GET'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def get_adafruit(slug):
    """Get Adafruit.io information."""
    try:
        adventure = Adventure.objects.get(slug=slug)
        if adventure.adafruit:
            return jsonify({'adafruit': adventure.adafruit.to_dict()})
        return jsonify({'error': 'Adafruit.io information is configured.'}), 400
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest:
        abort(400)
    return



@MOD_ADAFRUIT.route('/load', methods=['GET'])
@OAUTH.require_oauth('email')
def load_tracker(slug):
    """Load Adafruit.io tracker points from configured feed URL."""
    adventure = Adventure.objects().get(slug=slug)
    adafruit = adventure.adafruit
    if adafruit is not None:
        return load_data( \
            adafruit.base_url, adafruit.username, adafruit.feed, adafruit.aio_key, adventure \
        )
    return jsonify({'error': 'Adafruit.io configuration not found.'}), 500
