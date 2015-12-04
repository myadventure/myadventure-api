from flask import Response, Blueprint, request, abort
import logging
import bson
import json

from app.mod_config.models import Config

from app.mod_auth import oauth

mod_config = Blueprint('config', __name__, url_prefix='/api/v1/config')


@mod_config.route('/<name>', methods=['GET'])
@oauth.require_oauth('email')
def get_config(name):
    config = Config.objects(name=name).order_by('-date_added').first()
    if config is not None:
        return Response(bson.json_util.dumps(config.to_dict()), mimetype='application/json')
    else:
        return Response(bson.json_util.dumps({'error': 'configuration was not found.'}), status=400, mimetype='application/json')


@mod_config.route('', methods=['POST'])
@oauth.require_oauth('email')
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

    return Response(bson.json_util.dumps(config.to_dict()), mimetype='application/json')
