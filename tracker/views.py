"""
views.py

URL route handlers
"""

from flask import request, Response, abort, render_template, session, redirect, url_for, flash
from werkzeug.exceptions import BadRequest
from pykml import parser
from datetime import datetime
import urllib2
import time
import json
import bson
import logging
import delorme
import flickr_import
import instagram_import
import hashlib, uuid
import traceback

from models import Point, Config, User


def load_routes(app):

    @app.errorhandler(400)
    def bad_request(e):
        """Return a custom 400 error."""
        return 'The browser (or proxy) sent a request that this server could not understand.', 400


    @app.errorhandler(404)
    def page_not_found(e):
    	"""Return a custom 404 error."""
    	return 'Sorry, Nothing at this URL.', 404


    @app.errorhandler(500)
    def internal_error(e):
    	"""Return a custom 500 error."""
    	return 'Sorry, unexpected error: {}'.format(e), 500


    @app.route('/api/v1/point/route/load', methods=['POST'])
    def load_route():
        try:
            data = json.loads(request.data)
            url = data['url']
        except Exception as e:
            logging.error(0)
            abort(400)

        obj = urllib2.urlopen(url)
        str = obj.read()
        kml_str = ""
        for line in iter(str.splitlines()):
            if not 'atom:link' in line:
                kml_str+=line
                kml_str+='\n'

        Point.objects(type='route').delete()

        root = parser.fromstring(kml_str)

        pointid = 1000
        for placemark in root.Document.Folder.Placemark:
            coordinates = placemark.MultiGeometry.Point.coordinates.text.split(',')
            try:
                point = Point(
                    title = placemark.name.text,
                    type = 'route',
                    latitude = float(coordinates[1]),
                    longitude = float(coordinates[0]),
                    pointid = pointid,
                    timestamp = datetime.now()
                )
            except TypeError:
                abort(500)
            except Exception as e:
                logging.error(0)
                abort(500)
            try:
                point.save()
            except CapabilityDisabledError:
                logging.error(u'App Engine Datastore is currently in read-only mode.')
                abort(500)
            except Exception as e:
                logging.error(0)
                abort(500)

            pointid += 1

        return list_point('route')


    @app.route('/api/v1/point/<type>', methods=['GET'])
    def list_point(type):
        points_dict = None
        if points_dict is None:
            points_dict = []
            points = Point.objects(Point.type == type).order_by('timestamp', 'pointid')
            for point in points:
                points_dict.append(point.to_dict())

        return Response(bson.json_util.dumps(points_dict), mimetype='application/json');


    @app.route('/api/v1/point/<type>/<id>', methods=['GET'])
    def get_point(type, id):
        point = Point.objects.get(id=id)
        return Response(bson.json_util.dumps(point.to_dict()), mimetype='application/json');


    @app.route('/api/v1/point/<type>/<id>', methods=['PUT'])
    def update_point(type, id):
        point = Point.objects.get(id=id)

        try:
            data = json.loads(request.data)

            if 'title' in data:
                point.title = data['title']

            if 'latitude' in data:
                point.latitude = float(data['latitude'])

            if 'longitude' in data:
                point.longitude = float(data['longitude'])

            if 'desc' in data:
                point.desc = data['desc']

            if 'resource' in data:
                point.resource = data['resource']

            if 'thumb' in data:
                point.thumb = data['thumb']

            if 'photo' in data:
                point.photo = data['photo']

            if 'video' in data:
                point.video = data['video']

            if 'timestamp' in data:
                point.timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")

            if 'hide' in data:
                point.hide = bool(data['hide'])

            point.save()
        except TypeError:
            abort(400)
        except BadRequest as e:
            logging.error(e)
            abort(400)
        except Exception as e:
            logging.error(e)
            abort(500)

        return Response(bson.json_util.dumps(point.to_dict()), mimetype='application/json');


    @app.route('/api/v1/point/<type>', methods=['POST'])
    def add_point(type):
        try:
            data = json.loads(request.data)

            title = None
            if 'title' in data:
                title = data['title']

            if 'latitude' in data:
                latitude = float(data['latitude'])
            else:
                abort(400)

            if 'longitude' in data:
                longitude = float(data['longitude'])
            else:
                abort(400)

            desc = None
            if 'desc' in data:
                desc = data['desc']

            resource = None
            if 'resource' in data:
                resource = data['resource']

            thumb = None
            if 'thumb' in data:
                thumb = data['thumb']

            photo = None
            if 'photo' in data:
                photo = data['photo']

            video = None
            if 'video' in data:
                video = data['video']

            timestamp = datetime.now()
            if 'timestamp' in data:
                timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")

            point = Point(
                title=title,
                latitude=latitude,
                longitude=longitude,
                desc=desc,
                resource=resource,
                timestamp=timestamp,
                thumb=thumb,
                photo=photo,
                video=video,
                type=type
            )

            point.save()
        except TypeError:
            abort(400)
        except BadRequest as e:
            logging.error(e)
            abort(400)
        except Exception as e:
            logging.error(e)
            abort(500)

        return Response(bson.json_util.dumps(point.to_dict()), mimetype='application/json');


    @app.route('/api/v1/point/<type>/<id>', methods=['DELETE'])
    def delete_point(type, id):
        point = Point.objects.get(id=id)
        try:
            point.key.delete()
        except CapabilityDisabledError:
            logging.error(u'App Engine Datastore is currently in read-only mode.')
            abort(500)
        except Exception as e:
            logging.error(0)
            abort(500)

        return Response(bson.json_util.dumps({ 'status': 'ok' }), mimetype='application/json');


    @app.route('/api/v1/config/<name>', methods=['GET'])
    def get_config(name):
        config = Config.objects(name=name).order_by('-date_added').first()
        if config is not None:
            return Response(bson.json_util.dumps(config.to_dict()), mimetype='application/json');
        else:
            return Response(bson.json_util.dumps({ 'error': 'configuration was not found.' }), status=400, mimetype='application/json');


    @app.route('/api/v1/config', methods=['POST'])
    def save_config():
        try:
            data = json.loads(request.data)
            name = data['name']
            value = data['value']
            config = Config(
                name=name,
                value=value
            )
            config.save()
        except TypeError:
            abort(400)
        except Exception as e:
            logging.error(0)
            abort(500)

        return Response(bson.json_util.dumps(config.to_dict()), mimetype='application/json');


    @app.route('/api/v1/point/tracker/load', methods=['GET'])
    def load_tracker():
        tracker_url = Config.objects(name='tracker_url').order_by('-date_added').first()
        if tracker_url is None:
            return Response(bson.json_util.dumps({ 'error': 'tracker_url configuration was not found.' }), status=500, mimetype='application/json');

        tracker_type = Config.objects(name='tracker_type').order_by('-date_added').first()
        if tracker_type is None:
            return Response(bson.json_util.dumps({ 'error': 'tracker_type configuration was not found.' }), status=500, mimetype='application/json');

        if tracker_type.value == 'delorme':
            return delorme.load_data(tracker_url.value)
        elif tracker_type.value == 'spot':
            return Response(bson.json_util.dumps({ 'error': 'tracker not supported.' }), status=400, mimetype='application/json');
        else:
            return Response(bson.json_util.dumps({ 'error': 'tracker not supported.' }), status=400, mimetype='application/json');


    @app.route('/api/v1/user', methods=['POST'])
    def add_user():
        try:
            data = json.loads(request.data)
            email = data['email']
            password = data['password']
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(password + salt).hexdigest()
            user = User(
                email=email,
                password=hashed_password,
                salt=salt
            )
            user.save()
        except TypeError:
            abort(400)
        except Exception as e:
            logging.error(0)
            abort(500)

        return Response(bson.json_util.dumps({ "status": "ok" }), mimetype='application/json');


    @app.route('/api/v1/point/flickr/load', methods=['GET'])
    def load_flickr():
        user_id = Config.objects(name='flickr_username').order_by('-date_added').first()

        if user_id is None:
            return Response(bson.json_util.dumps({ 'error': 'flickr_username configuration was not found.' }), status=500, mimetype='application/json');

        photoset_id = Config.objects(name='flickr_photoset_title').order_by('-date_added').first()

        if photoset_id is None:
            return Response(bson.json_util.dumps({ 'error': 'flickr_photoset_title configuration was not found.' }), status=500, mimetype='application/json');

        api_key = Config.objects(name='flickr_api_key').order_by('-date_added').first()

        if api_key is None:
            return Response(bson.json_util.dumps({ 'error': 'flickr_api_key configuration was not found.' }), status=500, mimetype='application/json');

        api_secret = Config.objects(name='flickr_api_secret').order_by('-date_added').first()

        if api_secret is None:
            return Response(bson.json_util.dumps({ 'error': 'flickr_api_secret configuration was not found.' }), status=500, mimetype='application/json');

        return flickr_import.import_photos(user_id.value, photoset_id.value, api_key.value, api_secret.value)


    @app.route('/api/v1/point/instagram/load', methods=['GET'])
    def load_instagram():
        access_token = Config.objects(name='instagram_access_token').order_by('-date_added').first()

        if access_token is None:
            return Response(bson.json_util.dumps({ 'error': 'instagram_access_token configuration was not found.' }), status=500, mimetype='application/json');

        client_secret = Config.objects(name='instagram_client_secret').order_by('-date_added').first()

        if client_secret is None:
            return Response(bson.json_util.dumps({ 'error': 'instagram_client_secret configuration was not found.' }), status=500, mimetype='application/json');

        return instagram_import.import_media(access_token.value, client_secret.value)
