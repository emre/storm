# -*- coding: utf8 -*-

from ssh_config import ConfigParser
from exceptions import StormValueError


class Storm(object):

    def __init__(self, ssh_config_file=None):
        self.ssh_config = ConfigParser(ssh_config_file)
        self.ssh_config.load()

    def add_entry(self, name, host, user, port, id_file):
        if self.is_host_in(name):
            raise StormValueError('{0} is already in your sshconfig. use storm edit command to modify.'.format(name))

        options = self.get_options(host, user, port, id_file)

        self.ssh_config.add_host(name, options)
        self.ssh_config.write_to_ssh_config()

        return True

    def edit_entry(self, name, host, user, port, id_file):
        if not self.is_host_in(name):
            raise StormValueError('{0} doesn\'t exists in your sshconfig. use storm add command to add.'.format(name))

        options = self.get_options(host, user, port, id_file)
        self.ssh_config.update_host(name, options)
        self.ssh_config.write_to_ssh_config()

        return True

    def delete_entry(self, name):
        self.ssh_config.delete_host(name)
        self.ssh_config.write_to_ssh_config()

        return True

    def list_entries(self, order=False):
        if order:
            from operator import itemgetter
            config_data = sorted(self.ssh_config.config_data, key=itemgetter("host"))
            return config_data

        return self.ssh_config.config_data

    def delete_all_entries(self):
        self.ssh_config.delete_all_hosts()

        return True

    def get_options(self, host, user, port, id_file):
        options = {
            'hostname': host,
            'user': user,
            'port': port,
        }

        if id_file:
            options.update({
                'identityfile': id_file,
            })

        return options

    def is_host_in(self, host):
        for host_ in self.ssh_config.config_data:
            if host_.get("host") == host:
                return True
        return False
