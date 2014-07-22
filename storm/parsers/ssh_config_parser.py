# -*- coding: utf-8 -*-

from os import makedirs
from os import chmod
from os.path import dirname
from os.path import expanduser
from os.path import exists
from operator import itemgetter
import re

from paramiko.config import SSHConfig
import six



class StormConfig(SSHConfig):
    def parse(self, file_obj):
        """
        Read an OpenSSH config from the given file object.

        @param file_obj: a file-like object to read the config file from
        @type file_obj: file
        """
        order = 1
        host = {"host": ['*'], "config": {}, }
        for line in file_obj:
            line = line.rstrip('\n').lstrip()
            if line == '':
                self._config.append({
                    'type': 'empty_line',
                    'value': line,
                    'host': '',
                    'order': order,
                })
                order += 1
                continue

            if line.startswith('#'):
                self._config.append({
                    'type': 'comment',
                    'value': line,
                    'host': '',
                    'order': order,
                })
                order += 1
                continue

            if '=' in line:
                # Ensure ProxyCommand gets properly split
                if line.lower().strip().startswith('proxycommand'):
                    proxy_re = re.compile(r"^(proxycommand)\s*=*\s*(.*)", re.I)
                    match = proxy_re.match(line)
                    key, value = match.group(1).lower(), match.group(2)
                else:
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
            else:
                # find first whitespace, and split there
                i = 0
                while (i < len(line)) and not line[i].isspace():
                    i += 1
                if i == len(line):
                    raise Exception('Unparsable line: %r' % line)
                key = line[:i].lower()
                value = line[i:].lstrip()
            if key == 'host':
                self._config.append(host)
                value = value.split()
                host = {key: value, 'config': {}, 'type': 'entry', 'order': order}
                order += 1
            #identityfile is a special case, since it is allowed to be
            # specified multiple times and they should be tried in order
            # of specification.
            elif key in ['identityfile', 'localforward', 'remoteforward']:
                if key in host['config']:
                    host['config'][key].append(value)
                else:
                    host['config'][key] = [value]
            elif key not in host['config']:
                host['config'].update({key: value})
        self._config.append(host)


class ConfigParser(object):
    """
    Config parser for ~/.ssh/config files.
    """

    def __init__(self, ssh_config_file=None):
        if not ssh_config_file:
            ssh_config_file = self.get_default_ssh_config_file()

        self.defaults = {}

        self.ssh_config_file = ssh_config_file

        if not exists(self.ssh_config_file):
            if not exists(dirname(self.ssh_config_file)):
                makedirs(dirname(self.ssh_config_file))
            open(self.ssh_config_file, 'w+').close()
            chmod(self.ssh_config_file, 0o600)

        self.config_data = []

    def get_default_ssh_config_file(self):
        return expanduser("~/.ssh/config")

    def load(self):
        config = StormConfig()

        with open(self.ssh_config_file) as fd:
            config.parse(fd)

        for entry in config.__dict__.get("_config"):
            if entry.get("host") == ["*"]:
                self.defaults.update(entry.get("config"))

            if entry.get("type") in ["comment", "empty_line"]:
                self.config_data.append(entry)
                continue

            host_item = {
                'host': entry["host"][0],
                'options': entry.get("config"),
                'type': 'entry',
                'order': entry.get("order"),
            }

            if len(entry["host"]) > 1:
                host_item.update({
                    'host': " ".join(entry["host"]),
                })

            # minor bug in paramiko.SSHConfig that duplicates
            #"Host *" entries.
            if entry.get("config") and len(entry.get("config")) > 0:
                self.config_data.append(host_item)

        return self.config_data

    def add_host(self, host, options):
        self.config_data.append({
            'host': host,
            'options': options,
            'order': self.get_last_index(),
        })

        return self

    def update_host(self, host, options, use_regex=False):
        for index, host_entry in enumerate(self.config_data):
            if host_entry.get("host") == host or (use_regex and re.match(host, host_entry.get("host"))):
                self.config_data[index]["options"].update(options)
  
        return self

    def search_host(self, search_string):
        results = []
        for host_entry in self.config_data:
            if host_entry.get("type") != 'entry':
                continue
            if host_entry.get("host") == "*":
                continue

            searchable_information = host_entry.get("host")
            for key, value in six.iteritems(host_entry.get("options")):
                if isinstance(value, list):
                    value = " ".join(value)
                if isinstance(value, int):
                    value = str(value)

                searchable_information += " " + value

            if search_string in searchable_information:
                results.append(host_entry)

        return results

    def delete_host(self, host):
        found = 0
        for index, host_entry in enumerate(self.config_data):
            if host_entry.get("host") == host:
                del self.config_data[index]
                found += 1

        if found == 0:
            raise ValueError('No host found')
        return self

    def delete_all_hosts(self):
        self.config_data = []
        self.write_to_ssh_config()

        return self

    def dump(self):
        if len(self.config_data) < 1:
            return

        file_content = ""
        self.config_data = sorted(self.config_data, key=itemgetter("order"))

        for host_item in self.config_data:
            if host_item.get("type") in ['comment', 'empty_line']:
                file_content += host_item.get("value") + "\n"
                continue
            host_item_content = "Host {0}\n".format(host_item.get("host"))
            for key, value in six.iteritems(host_item.get("options")):
                if isinstance(value, list):
                    sub_content = ""
                    for value_ in value:
                        sub_content += "    {0} {1}\n".format(
                            key, value_
                        )
                    host_item_content += sub_content
                else:
                    host_item_content += "    {0} {1}\n".format(
                        key, value
                    )
            file_content += host_item_content

        return file_content

    def write_to_ssh_config(self):
        with open(self.ssh_config_file, 'w+') as f:
            data = self.dump()
            if data:
                f.write(data)
        return self

    def get_last_index(self):
        last_index = 0
        indexes = []
        for item in self.config_data:
            if item.get("order"):
                indexes.append(item.get("order"))
        if len(indexes) > 0:
            last_index = max(indexes)

        return last_index
