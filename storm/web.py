import json
import os.path

from flask import (Flask, Response, make_response, jsonify, request,
                   send_from_directory)

from storm import Storm, DELETED_SIGN
from storm.parsers.ssh_uri_parser import parse


app = Flask(__name__)
__THEME__ = "modern"


def render(template, theme):
    static_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(static_dir, 'templates', template)
    with open(path) as fobj:
        content = fobj.read()

    content = content.replace('__THEME__', request.args.get('theme', theme))

    return make_response(content)


def response(resp=None, status=200, content_type='application/json'):
    return Response(response=resp, status=status, content_type=content_type)


@app.route('/')
def index():
    return render('index.html', __THEME__)

@app.route('/list', methods=['GET'])
def list_keys():
    storm_ = app.get_storm()
    return response(json.dumps(storm_.list_entries(True, only_servers=True)))


@app.route('/add', methods=['POST'])
def add():
    storm_ = app.get_storm()

    try:
        name = request.json['name']
        connection_uri = request.json['connection_uri']
        id_file = None
        if 'id_file' in request.json:
            id_file = request.json['id_file']

        if '@' in name:
            msg = 'invalid value: "@" cannot be used in name.'
            return jsonify(message=msg), 400

        user, host, port = parse(connection_uri)
        storm_.add_entry(name, host, user, port, id_file)
        return response(status=201)
    except ValueError as exc:
        return jsonify(message=exc.message)
    except (KeyError, TypeError):
        return response(status=400)


@app.route('/edit', methods=['PUT'])
def edit():
    storm_ = app.get_storm()

    try:
        name = request.json['name']
        connection_uri = request.json['connection_uri']
        id_file = None
        if 'id_file' in request.json:
            id_file = request.json['id_file']
            if id_file == '':
                id_file = DELETED_SIGN

        user, host, port = parse(connection_uri)
        storm_.edit_entry(name, host, user, port, id_file)
        return response()
    except ValueError as exc:
        return jsonify(message=exc.message), 404
    except (KeyError, TypeError):
        return response(status=400)


@app.route('/delete', methods=['POST'])
def delete():
    storm_ = app.get_storm()

    try:
        name = request.json['name']
        storm_.delete_entry(name)
        return response()
    except ValueError as exc:
        return jsonify(message=exc.message), 404
    except (TypeError, ValueError):
        return response(status=400)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


def run(host, port, debug, theme, ssh_config=None):
    global __THEME__
    port = int(port)
    debug = bool(debug)
    host = str(host)
    __THEME__ = theme

    def get_storm():
        return Storm(ssh_config)

    app.get_storm = get_storm

    app.run(host=host, port=port, debug=debug)
