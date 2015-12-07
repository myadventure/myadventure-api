"""
controllers.py

Flickr module controllers.
"""
from flask import Response, Blueprint
import flickr_api
from datetime import datetime
import logging
import json
import bson

from app.mod_point.models import Point
from app.mod_auth import oauth

mod_flickr = Blueprint('flickr', __name__, url_prefix='/api/v1/flickr')


def import_photos(username, photoset_title, api_key, api_secret):
    flickr_api.set_keys(api_key=api_key, api_secret=api_secret)

    user = flickr_api.Person.findByUserName(username)
    photosets = user.getPhotosets()

    for photoset in iter(photosets):
        if photoset.title == photoset_title:
            photos = photoset.getPhotos()
            for photo in iter(photos):
                photo_id = int(photo.id)
                point = Point.objects(pointid=photo_id).first()
                if point is None:
                    latitude = None
                    longitude = None
                    title = photo.title
                    photopage = None
                    info = photo.getInfo()
                    taken = info[u'taken']
                    timestamp = datetime.strptime(taken, "%Y-%m-%d %H:%M:%S")
                    urls = info[u'urls'][u'url']
                    for url in urls:
                        if url[u'type'] == 'photopage':
                            photopage = url[u'text']
                            break
                    if u'location' in info:
                        location = info[u'location']
                        # locality = location[u'locality']
                        # region = location[u'region']
                        # country = location[u'country']
                        latitude = float(location[u'latitude'])
                        longitude = float(location[u'longitude'])
                        # title =  "%s, %s, %s" % (locality, region, country)
                    sizes = photo.getSizes()
                    thumb_url = sizes[u'Square'][u'source']
                    photo_url = sizes[u'Medium'][u'source']

                    try:
                        point = Point(
                            title=title,
                            latitude=latitude,
                            longitude=longitude,
                            type="photo",
                            timestamp=timestamp,
                            pointid=photo_id,
                            thumb=thumb_url,
                            photo=photo_url,
                            resource=photopage
                        )
                        point.save()
                    except AttributeError:
                        pass
                    except Exception as e:
                        logging.error(e.args[0])

    return Response(json.dumps({'status': 'ok'}), status=200, mimetype='application/json')


@mod_flickr.route('/load', methods=['GET'])
@oauth.require_oauth('email')
def load_flickr():
    # TODO: find flickr object by adventure
    user_id = Config.objects(name='flickr_username').order_by('-date_added').first()

    if user_id is None:
        return Response(bson.json_util.dumps({'error': 'flickr_username configuration was not found.'}), status=500,
                        mimetype='application/json')

    photoset_id = Config.objects(name='flickr_photoset_title').order_by('-date_added').first()

    if photoset_id is None:
        return Response(bson.json_util.dumps({'error': 'flickr_photoset_title configuration was not found.'}),
                        status=500, mimetype='application/json')

    api_key = Config.objects(name='flickr_api_key').order_by('-date_added').first()

    if api_key is None:
        return Response(bson.json_util.dumps({'error': 'flickr_api_key configuration was not found.'}), status=500,
                        mimetype='application/json')

    api_secret = Config.objects(name='flickr_api_secret').order_by('-date_added').first()

    if api_secret is None:
        return Response(bson.json_util.dumps({'error': 'flickr_api_secret configuration was not found.'}), status=500,
                        mimetype='application/json')

    return import_photos(user_id.value, photoset_id.value, api_key.value, api_secret.value)
