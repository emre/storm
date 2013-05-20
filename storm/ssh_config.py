# -*- coding: utf8 -*-

from os.path import expanduser
from paramiko.config import SSHConfig


class ConfigParser(object):
    """
    Config parser for ~/.ssh/config files.
    """

    def __init__(self, ssh_config_file=None):
        if not ssh_config_file:
            ssh_config_file = self.get_default_ssh_config_file()
        self.ssh_config_file = ssh_config_file

        self.config_data = []

    def get_default_ssh_config_file(self):
        return expanduser("~/.ssh/config")

    def load(self):
        config = SSHConfig()
        config.parse(open(self.ssh_config_file))
        for entry in config.__dict__.get("_config"):
            host_item = {
                'host': entry["host"][0],
                'options': entry["config"],
            }

            # minor bug in paramiko.SSHConfig that duplicates "Host *" entries.
            if len(entry["config"]) > 0:
                self.config_data.append(host_item)

        return self.config_data

    def dump(self):
        if len(self.config_data) < 1:
            return

        file_content = ""
        for host_item in self.config_data:
            host_item_content = "Host {0}\n".format(host_item.get("host"))
            for key, value in host_item.get("options").iteritems():
                host_item_content += "    {0} {1}\n".format(
                    key, value
                )
            file_content += host_item_content

        return file_content

