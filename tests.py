from __future__ import unicode_literals

import getpass
import os
import shlex
import subprocess
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import six

from storm import Storm
from storm.ssh_uri_parser import parse
from storm.exceptions import StormInvalidPortError


class StormCliTestCase(unittest.TestCase):

    def run_cmd(self, cmd):
        cmd = 'storm %s' % cmd
        cmd = shlex.split(cmd.encode('utf-8') if six.PY2 else cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, err = process.communicate()
        rc = process.returncode
        return out, err, rc

    def test_list_command(self):
        out, err, rc = self.run_cmd('list')
        self.assertEqual(out, b'\x1b[37mlisting entries:\n\n\x1b[0m\n')
        self.assertEqual(err, b'')
        self.assertEqual(rc, 0)


class StormTests(unittest.TestCase):

    def setUp(self):
        FAKE_SSH_CONFIG = """Host *
            IdentitiesOnly yes

        Host netscaler
            hostname 1.1.1.1
            port 3367

        """

        with open('/tmp/ssh_config', 'w+') as f:
            f.write(FAKE_SSH_CONFIG)

        self.storm = Storm('/tmp/ssh_config')

    def test_config_load(self):
        self.assertEqual(self.storm.ssh_config.config_data[1]["options"]["identitiesonly"], 'yes')

    def test_config_dump(self):
        self.storm.ssh_config.write_to_ssh_config()

        for search_str in ("hostname 1.1.1.1", "Host netscaler", "Host *"):
            with open('/tmp/ssh_config') as fd:
                self.assertIn(search_str, fd.read())

    def test_update_host(self):
        self.storm.ssh_config.update_host("netscaler", {"hostname": "2.2.2.2"})
        self.assertEqual(self.storm.ssh_config.config_data[4]["options"]["hostname"], '2.2.2.2')

    def test_add_host(self):
        self.storm.add_entry('google', 'google.com', 'root', '22', '/tmp/tmp.pub')
        self.storm.add_entry('goog', 'google.com', 'root', '22', '/tmp/tmp.pub')
        self.storm.ssh_config.write_to_ssh_config()

        for item in self.storm.ssh_config.config_data:
            if item.get("host") == 'google' or item.get("host") == 'goog':
                self.assertEqual(item.get("options").get("port"), '22')
                self.assertEqual(item.get("options").get("identityfile"), '/tmp/tmp.pub')

    def test_edit_host(self):

        self.storm.add_entry('google', 'google.com', 'root', '22', '/tmp/tmp.pub')
        self.storm.ssh_config.write_to_ssh_config()

        self.storm.edit_entry('google', 'google.com', 'root', '23', '/tmp/tmp.pub')
        self.storm.ssh_config.write_to_ssh_config()

        for item in self.storm.ssh_config.config_data:
            if item.get("host") == 'google':
                self.assertEqual(item.get("options").get("port"), '23')

    def test_edit_by_hostname_regexp(self):
        import re
        self.storm.add_entry('google-01', 'google.com', 'root', '22', '/tmp/tmp.pub')
        self.storm.add_entry('google-02', 'google.com', 'root', '23', '/tmp/tmp.pub')
        self.storm.ssh_config.write_to_ssh_config()

        self.storm.update_entry('google-[0-2]', port='24', identityfile='/tmp/tmp.pub1')

        for item in self.storm.ssh_config.config_data:
            if re.match(r"google*", item.get("host")):
                self.assertEqual(item.get("options").get("identityfile"), '/tmp/tmp.pub1')
                self.assertEqual(item.get("options").get("port"), '24')

    def test_delete_host(self):
        self.storm.delete_entry('netscaler')
        for host in self.storm.ssh_config.config_data:
            self.assertEqual(False, host.get("host") == 'netscaler')

    def test99_delete_all(self):
        self.storm.delete_all_entries()
        self.assertEqual(len(self.storm.ssh_config.config_data), 0)

    def test_uri_parser(self):
        user = getpass.getuser()
        TEST_STRINGS = [
            ('root@emreyilmaz.me:22', ('root', 'emreyilmaz.me', 22)),
            ('emreyilmaz.me', (user, 'emreyilmaz.me', 22)),
            ('emreyilmaz.me:22', (user, 'emreyilmaz.me', 22)),
            ('root@emreyilmaz.me', ('root', 'emreyilmaz.me', 22))
        ]

        for uri in TEST_STRINGS:
            self.assertEqual(parse(uri[0]), uri[1])

        # false strings
        self.assertRaises(StormInvalidPortError, parse, 'root@emreyilmaz.me:string-port')

    def test_search_host(self):
        results = self.storm.ssh_config.search_host("netsca")
        self.assertEqual(len(results), 1)

    def test_custom_options(self):
        custom_options = (
            "StrictHostKeyChecking=no",
            "UserKnownHostsFile=/dev/null",
        )
        self.storm.add_entry('host_with_custom_option',
                             'emre.io', 'emre', 22,
                             None, custom_options=custom_options)
        self.storm.ssh_config.write_to_ssh_config()

        for item in self.storm.ssh_config.config_data:
            if item.get("host") == 'host_with_custom_option':
                self.assertEqual(item.get("options").get("StrictHostKeyChecking"), 'no')
                self.assertEqual(item.get("options").get("UserKnownHostsFile"), '/dev/null')

        custom_options = (
            "StrictHostKeyChecking=yes",
            "UserKnownHostsFile=/home/emre/foo",
        )
        self.storm.edit_entry('host_with_custom_option',
                              'emre.io', 'emre', 22,
                              None, custom_options=custom_options)
        self.storm.ssh_config.write_to_ssh_config()

        for item in self.storm.ssh_config.config_data:
            if item.get("host") == 'host_with_custom_option':
                self.assertEqual(item.get("options").get("StrictHostKeyChecking"), 'yes')
                self.assertEqual(item.get("options").get("UserKnownHostsFile"), '/home/emre/foo')

    def tearDown(self):
        os.unlink('/tmp/ssh_config')

if __name__ == '__main__':
    unittest.main()
