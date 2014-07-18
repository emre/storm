#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys


try:
    import __builtin__ as builtins
except ImportError:
    import builtins

import getpass
import collections

import six

from storm import Storm, __version__
from storm.exceptions import StormValueError
from storm.ssh_uri_parser import parse
from storm import web as _web
from storm.utils import (get_formatted_message, fixed_width, colored)
from storm.kommandr import *

default_user = getpass.getuser()


def get_storm_instance(config_file=None):
    return Storm(config_file)


@command('version')
def version():
    """
    prints the working storm(ssh) version.
    """
    print(__version__)


@command('add')
def add(name, connection_uri, id_file="", o=[], config=None):
    """
    Adds a new entry to sshconfig.
    """
    storm_ = get_storm_instance(config)

    try:

        # validate name
        if '@' in name:
            raise StormValueError('invalid value: "@" cannot be used in name.')
        user, host, port = parse(connection_uri)
        storm_.add_entry(name, host, user, port, id_file, o)

        print(get_formatted_message('{0} added to your ssh config. you can connect it by typing "ssh {0}".'.format(

            name
        ), 'success'))

    except StormValueError as error:
        print(get_formatted_message(error, 'error'), file=sys.stderr)


@command('clone')
def clone(name, clone_name, config=None):
    """
    Clone an entry to the sshconfig.
    """
    storm_ = get_storm_instance(config)

    try:

        # validate name
        if '@' in name:
            raise StormValueError('invalid value: "@" cannot be used in name.')

        storm_.clone_entry(name, clone_name)

        print(get_formatted_message('{0} added to your ssh config. you can connect it by typing "ssh {0}".'.format(
            clone_name
        ), 'success'))

    except StormValueError as error:
        print(get_formatted_message(error, 'error'), file=sys.stderr)


@command('edit')
def edit(name, connection_uri, id_file="", o=[], config=None):
    """
    Edits the related entry in ssh config.
    """
    storm_ = get_storm_instance(config)

    try:
        if ',' in name:
            name = " ".join(name.split(","))

        user, host, port = parse(connection_uri)

        storm_.edit_entry(name, host, user, port, id_file, o)
        print(get_formatted_message(
            '"{0}" updated successfully.'.format(
                name
            ), 'success'))
    except StormValueError as error:
        print(get_formatted_message(error, 'error'), file=sys.stderr)

@command('update')
def update(name, connection_uri="", id_file="", o=[], config=None):
    """
    Enhanced version of the edit command featuring multiple edits using regular expressions to match entries
    """
    storm_ = get_storm_instance(config)
    settings = {}

    if id_file != "": 
        settings['identityfile'] = id_file

    for option in o:
        k, v = option.split("=")
        settings[k] = v

    try:
        storm_.update_entry(name, **settings)
        print(get_formatted_message(
            '"{0}" updated successfully.'.format(
                name
            ), 'success'))
    except StormValueError as error:
        print(get_formatted_message(error, 'error'), file=sys.stderr)

@command('delete')
def delete(name, config=None):
    """
    Deletes a single host.
    """
    storm_ = get_storm_instance(config)

    try:
        storm_.delete_entry(name)
        print(get_formatted_message('hostname "{0}" deleted successfully.'.format(name), 'success'))
    except StormValueError as error:
        print(get_formatted_message(error, 'error'), file=sys.stderr)

@command('list')
def list(config=None):
    """
    Lists all hosts from ssh config.
    """
    storm_ = get_storm_instance(config)

    try:
        result = colored('listing entries:\n\n', 'white')
        result_stack = ""
        for host in storm_.list_entries(True):

            if host.get("type") == 'entry':
                if not host.get("host") == "*":
                    result += "    {0} -> {1}@{2}:{3}".format(
                        colored(host["host"], 'white'),
                        host.get("options").get("user", default_user),
                        host.get("options").get("hostname", "[hostname_not_specified]"),
                        host.get("options").get("port", 22)
                    )

                    extra = False
                    for key, value in six.iteritems(host.get("options")):

                        if not key in ["user", "hostname", "port"]:
                            if not extra:
                                custom_options = colored('\n\t[custom options] ', 'white')
                                result += " {0}".format(custom_options)
                            extra = True

                            if isinstance(value, collections.Sequence):
                                if isinstance(value, builtins.list):
                                    value = ",".join(value)
                                    
                            result += "{0}={1} ".format(key, value)
                    if extra:
                        result = result[0:-1]

                    result += "\n\n"
                else:
                    result_stack = "  (*) -> "
                    for key, value in six.iteritems(host.get("options")):
                        if isinstance(value, type([])):
                            result_stack += "{0}:\n".format(key)
                            for value_ in value:
                                result_stack += "    {0}\n".format(
                                    value_
                                )
                        else:
                            result_stack += "    {0}:{1}\n".format(
                                key,
                                value,
                            )
                    result_stack = result_stack[0:-1] + "\n"

        result += result_stack
        print(result)
    except Exception as error:
        print(get_formatted_message(str(error), 'error'), file=sys.stderr)

@command('search')
def search(search_text, config=None):
    """
    Searches entries by given search text.
    """
    storm_ = get_storm_instance(config)

    try:
        results = storm_.search_host(search_text)
        if len(results) == 0:
            print ('no results found.')

        if len(results) > 0:
            message = 'Listing results for {0}:\n'.format(search_text)
            message += "".join(results)
            print(message)
    except Exception as error:
        print(get_formatted_message(str(error), 'error'), file=sys.stderr)

@command('delete_all')
def delete_all(config=None):
    """
    Deletes all hosts from ssh config.
    """
    storm_ = get_storm_instance(config)

    try:
        storm_.delete_all_entries()
        print(get_formatted_message('all entries deleted.', 'success'))
    except Exception as error:
        print(get_formatted_message(str(error), 'error'), file=sys.stderr)


@command('web')
def web(port=9002, debug=False, ssh_config=None):
    """Starts the web UI."""
    _web.run(port, debug, ssh_config)


if __name__ == '__main__':
    sys.exit(main())

