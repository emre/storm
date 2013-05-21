# -*- coding: utf8 -*-

from ssh_config import ConfigParser


class Storm(object):

    def __init__(self):
        ssh_config = ConfigParser()

    def add_entry(self):
        raise NotImplementedError

    def edit_entry(self):
        raise NotImplementedError

    def delete_entry(self):
        raise NotImplementedError

    def list_entries(self):
        raise NotImplementedError

    def delete_all(self):
        raise NotImplementedError