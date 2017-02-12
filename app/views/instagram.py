"""
instagram.py

Instagram views

"""

from __future__ import absolute_import

import logging
import urlparse
from instagram.client import InstagramAPI
from flask import Blueprint, abort, request, jsonify
from werkzeug.exceptions import BadRequest
from app.decorators import crossdomain
from app.views.auth import OAUTH
from app.models.adventure import Adventure
from app.models.instagram import Instagram
from app.models.point import Point

MOD_INSTAGRAM = Blueprint('instagram', __name__, url_prefix='/api/v1/adventure/<slug>/instagram')


def get_media(api, media=None, max_id=None):
    """Get media."""

    if media is None:
        media = []

    response, next_url = api.user_recent_media(max_id=max_id)

    for media_item in response:
        media.append(media_item)

    # TODO: Pagination is not working as expected.
    # The client is expecting a next_url parameter in the pagination object,
    # but even with more pictures to load, nothing is being returned.
    if next_url is not None:
        parsednext = urlparse.urlparse(next)
        max_id = urlparse.parse_qs(parsednext.query)['max_id'][0]
        media = get_media(api, media, max_id)

    return media


def import_media(access_token, client_secret, adventure):
    """Import media."""

    api = InstagramAPI( \
        access_token=access_token.encode('ascii', 'ignore'), \
        client_secret=client_secret.encode('ascii', 'ignore') \
    )

    media = get_media(api)

    for item in media:
        title = None
        desc = None
        video = None
        latitude = None
        longitude = None
        if hasattr(item, 'caption'):
            if item.caption is not None:
                desc = item.caption.text
        if hasattr(item, 'location'):
            if item.location.name is not None:
                title = item.location.name
            if item.location.point is not None:
                latitude = item.location.point.latitude
                longitude = item.location.point.longitude
        timestamp = item.created_time
        media_type = item.type
        if media_type == 'image':
            media_type = 'photo'
        thumb = item.images.get('thumbnail').url
        photo = item.images.get('standard_resolution').url
        if hasattr(item, 'videos'):
            video = item.videos.get('standard_resolution').url
        resource = item.link

        if item.id is not None:
            point = adventure.points.filter( \
                point_type=media_type, instagram_id=item.id \
            ).first()

            if point is None:
                point = Point(
                    title=title,
                    desc=desc,
                    elevation=None,
                    speed=None,
                    direction=None,
                    latitude=latitude,
                    longitude=longitude,
                    resource=resource,
                    point_type=media_type,
                    timestamp=timestamp,
                    delorme_id=None,
                    aio_id=None,
                    instagram_id=item.id,
                    hide=False,
                    thumb=thumb,
                    photo=photo,
                    video=video
                )

                adventure.points.append(point)
                adventure.save()

    return jsonify({'status': 'ok'})


@MOD_INSTAGRAM.route('/', methods=['POST'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def add_instagram(slug):
    """Add Instagram configuration to Adventure object defined by slug."""
    try:
        adventure = Adventure.objects.get(slug=slug)
        access_token = request.values.get('access_token', None)
        client_secret = request.values.get('client_secret', None)

        adventure.instagram = Instagram(
            access_token=access_token,
            client_secret=client_secret
        )
        adventure.save()

        return jsonify({'status': 'ok'})
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest:
        abort(400)
    return


@MOD_INSTAGRAM.route('/', methods=['GET'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def get_instagram(slug):
    """Get Instagram information."""
    try:
        adventure = Adventure.objects.get(slug=slug)
        if adventure.instagram:
            return jsonify({'instagram': adventure.instagram.to_dict()})
        return jsonify({'error': 'Instagram is not configured for this adventure.'}), 400
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest:
        abort(400)
    return



@MOD_INSTAGRAM.route('/load', methods=['GET'])
@OAUTH.require_oauth('email')
def load_tracker(slug):
    """Load Instagram photo feed."""
    adventure = Adventure.objects().get(slug=slug)
    instagram = adventure.instagram
    if instagram is not None:
        return import_media(instagram.access_token, instagram.client_secret, adventure)
    return jsonify({'error': 'Instagram is not configured for this adventure.'}), 500
