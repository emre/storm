# -*- coding: utf8 -*-


class StormValueError(ValueError):
    pass

class NoHostname(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Could not parse host: "+repr(self.value)+'\tNo Hostname entry'
