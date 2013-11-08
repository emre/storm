import json
import os.path

from flask import Flask, make_response, jsonify, request

from storm import Storm
from storm.ssh_uri_parser import parse
from storm.exceptions import StormValueError

app = Flask(__name__)
storm_ = Storm()


def render(template):
    path = os.path.join('storm', 'templates', template)
    with open(path) as fobj:
        content = fobj.read()
    return make_response(content)


@app.route('/')
def index():
    return render('index.html')


@app.route('/list', methods=['GET'])
def list_keys():
    return json.dumps(storm_.list_entries(True))


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

        return '', 201
    except StormValueError as exc:
        return jsonify(message=exc.message)
    except (KeyError, TypeError):
        return '', 400


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

        return '', 200
    except StormValueError as exc:
        return jsonify(message=exc.message), 404
    except (KeyError, TypeError):
        return '', 400


@app.route('/delete', methods=['DELETE'])
def delete():
    try:
        name = request.json['name']
        storm_.delete_entry(name)
        return '', 200
    except StormValueError as exc:
        return jsonify(message=exc.message), 404
    except (TypeError, StormValueError):
        return '', 400


@app.route('/delete_all', methods=['DELETE'])
def delete_all():
    try:
        storm_.delete_all_entries()
        return '', 200
    except StormValueError:
        return '', 400


def run(port, debug):
    app.run(port=port, debug=debug)
