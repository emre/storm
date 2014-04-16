# -*- coding: utf-8 -*-

from os.path import expanduser
from os.path import exists

import json


def get_storm_config():
    config_file = expanduser("~/.stormssh/config")

    if exists(config_file):
        try:
            config_data = json.loads(open(config_file).read())
            return config_data

        except Exception as error:
            pass
    return {}
