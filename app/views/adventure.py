"""
Adventure view

"""

import logging
from flask import Blueprint, jsonify, abort, request
from mongoengine import DoesNotExist
from werkzeug.exceptions import BadRequest
from slugify import slugify
from app.decorators import crossdomain
from app.views.auth import OAUTH
from app.models.adventure import Adventure

MOD_ADVENTURE = Blueprint('adventure', __name__, url_prefix='/api/v1/adventure')

@MOD_ADVENTURE.route('/', methods=['GET'])
@crossdomain(origin='*')
def list_adventures():
    """List all Adventures."""
    adventures_dict = []
    try:
        adventures = Adventure.objects()
        for adventure in adventures:
            adventures_dict.append(adventure.to_dict())
    except DoesNotExist as err:
        logging.info(err)

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
@OAUTH.require_oauth('email')
def add_adventure():
    """Add Adventure."""
    try:
        name = request.values.get('name', None)
        description = request.values.get('description', None)
        user = request.oauth.user
        adventure = Adventure(
            slug=slugify(name),
            name=name,
            description=description,
            users=[user],
            delorme=None,
            adafruit=None,
            points=[]
        )
        adventure.save()

        return jsonify(adventure.to_dict())
    except TypeError as err:
        logging.error(err)
        abort(400)
    except BadRequest:
        abort(400)
    return


@MOD_ADVENTURE.route('/<slug>', methods=['DELETE'])
@crossdomain(origin='*')
@OAUTH.require_oauth('email')
def delete_point(slug):
    """Delete Adventure."""
    adventure = Adventure.objects.get(slug=slug)
    try:
        adventure.delete()
        return jsonify({'status': 'ok'})
    except DoesNotExist:
        abort(404)
    return
