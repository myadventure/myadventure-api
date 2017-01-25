"""
Initialize adventure controller

"""

import logging
from flask import jsonify, abort, request
from mongoengine import DoesNotExist
from werkzeug.exceptions import BadRequest
from slugify import slugify
from app.decorators import crossdomain
from app.mod_auth.controllers import oauth
from app.mod_adventure.models.adventure import Adventure
from app.mod_adventure.controllers import MOD_ADVENTURE

@MOD_ADVENTURE.route('/', methods=['GET'])
@crossdomain(origin='*')
def list_adventures():
    """List all Adventures."""
    adventures = Adventure.objects()
    adventures_dict = []
    for adventure in adventures:
        adventures_dict.append(adventure.to_dict())
    return jsonify(adventures=adventures_dict)


@MOD_ADVENTURE.route('/<slug>', methods=['GET'])
@crossdomain(origin='*')
def get_adventure(slug):
    """Get Adventure."""
    try:
        adventure = Adventure.objects.get(slug=slug)
        return jsonify(adventure.to_dict())
    except DoesNotExist:
        abort(404)
    return


@MOD_ADVENTURE.route('/', methods=['POST'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def add_adventure():
    """Add Adventure."""
    try:
        name = request.values.get('name', None)
        user = request.oauth.user
        adventure = Adventure(
            slug=slugify(name),
            name=name,
            users=[user],
            delorme=None,
            points=[]
        )
        adventure.save()

        return jsonify(adventure.to_mongo())
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest:
        abort(400)
    return


@MOD_ADVENTURE.route('/<slug>', methods=['DELETE'])
@crossdomain(origin='*')
@oauth.require_oauth('email')
def delete_point(slug):
    """Delete Adventure."""
    adventure = Adventure.objects.get(slug=slug)
    try:
        adventure.delete()
        return jsonify(adventure.to_mongo())
    except DoesNotExist:
        abort(404)
    return
