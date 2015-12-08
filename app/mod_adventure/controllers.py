"""
controllers.py

Adventure module controllers.
"""
from flask import Blueprint, jsonify, request, abort
from werkzeug.exceptions import BadRequest
import logging
from slugify import slugify

from app.mod_adventure.models import Adventure
from app.mod_user.models import User
from app.mod_auth import oauth
from app.decorators import crossdomain

mod_adventure = Blueprint('adventure', __name__, url_prefix='/api/v1/adventure')


@mod_adventure.route('/', methods=['GET'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def list_adventures():
    user = request.oauth.user
    adventures = user.adventures
    adventures_dict = []
    for adventure in adventures:
        print adventure.to_mongo()
    return jsonify({})


@mod_adventure.route('/<slug>', methods=['GET'])
@crossdomain(origin='*')
def get_adventure(slug):
    adventure = Adventure.objects.get(slug=slug)
    return jsonify(adventure.to_mongo())


@mod_adventure.route('/', methods=['POST'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def add_adventure():
    try:
        name = request.values.get('name')
        user = request.oauth.user
        adventure = Adventure(
            slug=slugify(name),
            name=name
        )
        adventure.save()
        user.update(add_to_set__adventures=[adventure])

        return jsonify(adventure.to_mongo())
    except TypeError as e:
        logging.error(e)
        abort(400)
    except BadRequest:
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)

    return


@mod_adventure.route('/<slug>', methods=['DELETE'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def delete_point(slug):
    adventure = Adventure.objects(slug=slug)
    try:
        adventure.delete()
        User.objects(adventures__id=adventure.id).update(pull__adventures=adventure)
        return jsonify(adventure.to_mongo())
    except TypeError:
        abort(400)
    except BadRequest:
        abort(400)
    except Exception as e:
        logging.error(e)
        abort(500)

    return
