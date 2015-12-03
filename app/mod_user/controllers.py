from flask import Response, Blueprint, request, abort, session
import hashlib
import uuid
import json
import bson
import logging

from app.mod_user.models import User

mod_user = Blueprint('user', __name__, url_prefix='/api/v1/user')


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.objects(email=uid).first()
    return None


@mod_user.route('', methods=['POST'])
def add_user():
    try:
        data = json.loads(request.data)
        email = data['email']
        # password = data['password']
        # salt = uuid.uuid4().hex
        # hashed_password = hashlib.sha512(password + salt).hexdigest()
        user = User(
            email=email,
            # password=hashed_password,
            # salt=salt
        )
        user.save()
    except TypeError:
        abort(400)
    except Exception as e:
        logging.error(0)
        abort(500)

    return Response(bson.json_util.dumps({"status": "ok"}), mimetype='application/json')
