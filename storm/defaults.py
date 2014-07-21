# -*- coding: utf-8 -*-

import getpass

DEFAULT_PORT = 22
DEFAULT_USER = getpass.getuser()


def get_default(key, defaults={}):

    if key == 'port':
        return defaults.get("port", DEFAULT_PORT)

    if key == 'user':
        return defaults.get("user", DEFAULT_USER)

    return defaults.get(key)