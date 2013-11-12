import json
import os.path

from flask import Flask, Response, make_response, jsonify, request

from storm import Storm
from storm.ssh_uri_parser import parse
from storm.exceptions import StormValueError

app = Flask(__name__)
storm_ = Storm()


def render(template):
    static_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(static_dir, 'templates', template)
    with open(path) as fobj:
        content = fobj.read()
    return make_response(content)


def response(resp=None, status=200, content_type='application/json'):
    return Response(response=resp, status=status, content_type=content_type)


@app.route('/')
def index():
    return render('index.html')


@app.route('/list', methods=['GET'])
def list_keys():
    return response(json.dumps(storm_.list_entries(True)))


@app.route('/add', methods=['POST'])
def add():
    try:
        name = request.json['name']
        connection_uri = request.json['connection_uri']
        if 'id_file' in request.json:
            id_file = request.json['id_file']
        else:
            id_file = ''

        if '@' in name:
            msg = 'invalid value: "@" cannot be used in name.'
            return jsonify(message=msg), 400

        user, host, port = parse(connection_uri)
        storm_.add_entry(name, host, user, port, id_file)
        return response(status=201)
    except StormValueError as exc:
        return jsonify(message=exc.message)
    except (KeyError, TypeError):
        return response(status=400)


@app.route('/edit', methods=['PUT'])
def edit():
    try:
        name = request.json['name']
        connection_uri = request.json['connection_uri']
        if 'id_file' in request.json:
            id_file = request.json['id_file']
        else:
            id_file = ''

        user, host, port = parse(connection_uri)
        storm_.edit_entry(name, host, user, port, id_file)
        return response()
    except StormValueError as exc:
        return jsonify(message=exc.message), 404
    except (KeyError, TypeError):
        return response(status=400)


@app.route('/delete', methods=['DELETE'])
def delete():
    try:
        name = request.json['name']
        storm_.delete_entry(name)
        return response()
    except StormValueError as exc:
        return jsonify(message=exc.message), 404
    except (TypeError, StormValueError):
        return response(status=400)


@app.route('/delete_all', methods=['DELETE'])
def delete_all():
    try:
        storm_.delete_all_entries()
        return response()
    except StormValueError:
        return response(status=400)


def run(port, debug):
    app.run(port=port, debug=debug)
