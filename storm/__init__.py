# -*- coding: utf8 -*-

from ssh_config import ConfigParser
from exceptions import StormValueError


class Storm(object):

    def __init__(self):
        self.ssh_config = ConfigParser()
        self.ssh_config.load()

    def add_entry(self, name, host, user, port):
        if self.is_host_in(name):
            raise StormValueError('{0} is already in your sshconfig. use storm edit command to modify.'.format(name))

        options = self.get_options(host, user, port)

        self.ssh_config.add_host(name, options)
        self.ssh_config.write_to_ssh_config()

        return True

    def edit_entry(self, name, host, user, port):
        if not self.is_host_in(name):
            raise StormValueError('{0} doesn\'t exists in your sshconfig. use storm add command to add.'.format(name))

        options = self.get_options(host, user, port)
        self.ssh_config.update_host(name, options)
        self.ssh_config.write_to_ssh_config()

        return True

    def delete_entry(self):
        raise NotImplementedError

    def list_entries(self):
        raise NotImplementedError

    def delete_all(self):
        raise NotImplementedError

    def get_options(self, host, user, port):
        return {
            'Hostname': host,
            'user': user,
            'port': port,
        }

    def is_host_in(self, host):
        for host_ in self.ssh_config.config_data:
            if host_.get("host") == host:
                return True
        return False
