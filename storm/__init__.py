# -*- coding: utf8 -*-


class HostEntry(object):

    def __init__(self, name, host, user, port=22):
        self.name = name
        self.host = host
        self.user = user
        self.port = port

    def write_to_config(self):
        raise NotImplementedError