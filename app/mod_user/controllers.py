from flask import Response, Blueprint
import hashlib, uuid

mod_user = Blueprint('user', __name__, url_prefix='/api/v1/user')

from app.mod_user.models import User

@mod_user.route('', methods=['POST'])
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
