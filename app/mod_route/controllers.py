from flask import Response, Blueprint

from app.mod_point.models import Point

mod_route = Blueprint('route', __name__, url_prefix='/api/v1/route')

@mod_route.route('/load', methods=['POST'])
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
        except TypeError:
            abort(400)
        except BadRequest as e:
            logging.error(e)
            abort(400)
        except Exception as e:
            logging.error(e)
            abort(500)

        pointid += 1

    return list_point('route')
