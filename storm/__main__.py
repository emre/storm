# -*- coding: utf8 -*-

#!/usr/bin/python

import sys

import getpass
import __builtin__

from storm import Storm, __version__
from storm.exceptions import StormValueError
from storm.ssh_uri_parser import parse
from storm import web as _web

from storm.kommandr import *

from termcolor import colored

storm_ = Storm()

default_user = getpass.getuser()


def fixed_width(text, size):
    text_width = len(text)
    if size > text_width:
        for _ in range(text_width, size):
            text += " "

    return text


def get_formatted_message(message, format_type):
    format_typed = fixed_width(format_type, 8)
    all_message = ""
    message = " %s" % message

    if format_type == 'error':
        all_message = colored(format_typed, 'white', 'on_red')
    if format_type == 'success':
        all_message = colored(format_typed, 'white', 'on_green')

    return all_message+message


@command('version')
def version():
    """
    prints the working storm(ssh) version.
    """
    print __version__


@command('add')
def add(name, connection_uri, id_file="", o=[]):
    """
    Adds a new entry to sshconfig.
    """
    try:

        # validate name
        if '@' in name:
            raise StormValueError('invalid value: "@" cannot be used in name.')
        user, host, port = parse(connection_uri)

        storm_.add_entry(name, host, user, port, id_file, o)

        print get_formatted_message('{0} added to your ssh config. you can connect it by typing "ssh {0}".'.format(

            name
        ), 'success')

    except StormValueError as error:
        print get_formatted_message(error, 'error')


@command('edit')
def edit(name, connection_uri, id_file="", o=[]):
    """
    Edits the related entry in ssh config.
    """
    try:
        if ',' in name:
            name = " ".join(name.split(","))

        user, host, port = parse(connection_uri)

        storm_.edit_entry(name, host, user, port, id_file, o)
        print get_formatted_message(
            '"{0}" updated successfully.'.format(
                name
            ), 'success')
    except StormValueError as error:
        print get_formatted_message(error, 'error')

@command('delete')
def delete(name):
    """
    Deletes a single host.
    """
    try:
        storm_.delete_entry(name)
        print get_formatted_message('hostname "{0}" deleted successfully.'.format(name), 'success')
    except StormValueError as error:
        print get_formatted_message(error, 'error')

@command('list')
def list():
    """
    Lists all hosts from ssh config.
    """
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
                    for key, value in host.get("options").iteritems():

                        if not key in ["user", "hostname", "port"]:
                            if not extra:
                                custom_options = colored('\n\t[custom options] ', 'white')
                                result += " {0}".format(custom_options)
                            extra = True

                            if isinstance(value, __builtin__.list):
                                value = ",".join(value)

                            result += "{0}={1} ".format(key, value)
                    if extra:
                        result = result[0:-1]

                    result += "\n\n"
                else:
                    result_stack = "  (*) -> "
                    for key, value in host.get("options").iteritems():
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
                    result_stack = result_stack[0:-2] + "\n"

        result += result_stack
        print result
    except Exception as error:
        print get_formatted_message(str(error), 'error')

@command('search')
def search(search_text):
    """
    Searches entries by given search text.
    """
    try:
        results = storm_.search_host(search_text)
        if len(results) == 0:
            print ('no results found.')

        if len(results) > 0:
            message = 'Listing results for {0}:\n'.format(search_text)
            message += "".join(results)
            print message
    except Exception as error:
        print get_formatted_message(str(error), 'error')

@command('delete_all')
def delete_all():
    """
    Deletes all hosts from ssh config.
    """
    try:
        storm_.delete_all_entries()
        print get_formatted_message('all entries deleted.', 'success')
    except Exception as error:
        print get_formatted_message(str(error), 'error')


@command('web')
def web(port=9002, debug=False):
    """Starts the web UI."""
    _web.run(port, debug)


if __name__ == '__main__':
    sys.exit(main())

