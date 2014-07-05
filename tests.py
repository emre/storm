import getpass
import os
from tempfile import NamedTemporaryFile
import mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from storm import Storm, __version__
from storm.ssh_uri_parser import parse
from storm.exceptions import StormInvalidPortError
from storm.__main__ import version, search, delete_all


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


class StormMainCommandsTests(unittest.TestCase):

    def setUp(self):
        config_content = """Host *
            IdentitiesOnly yes

        Host netscaler
            hostname 1.1.1.1
            port 3367

        Host nestcaller
            user caller
            hostname 2.2.2.2
            port 22222
            LocalForward 3128 127.0.0.1:3128
            IdentityFile ~/.ssh/global1.key
            ProxyCommand /usr/bin/nc -X connect -x 192.168.0.1:3128 %h %p

        """

        self.test_config_fh = NamedTemporaryFile(
            prefix="stormssh_test_sshd_config-", mode="w+", delete=False)
        self.test_config_fh.write(config_content)
        self.test_config_fh.close()

        self.storm = Storm(self.test_config_fh.name)

    def tearDown(self):
        if os.path.exists(self.test_config_fh.name):
            self.test_config_fh.close()
            os.unlink(self.test_config_fh.name)

    @mock.patch('__builtin__.print')
    def test_version(self, mk_print):
        version()
        mk_print.assert_called_once_with(__version__)

    @mock.patch('storm.__main__.get_storm_instance')
    @mock.patch('__builtin__.print')
    def test_search(self, mk_print, mk_gsi):
        results = ['    nestcaller -> caller@2.2.2.2:22222\n']
        mk_gsi.return_value.search_host.return_value = results

        search("nest", self.storm.ssh_config)

        mk_gsi.assert_called_once_with(self.storm.ssh_config)
        mk_gsi.return_value.search_host.assert_called_once_with("nest")

        message = 'Listing results for nest:\n'
        message += "".join(results)

        mk_print.assert_called_once_with(message)

    @mock.patch('storm.__main__.get_formatted_message')
    @mock.patch('storm.__main__.get_storm_instance')
    @mock.patch('__builtin__.print')
    def test_delete_all(self, mk_print, mk_gsi, mk_gfm):
        delete_all(self.storm.ssh_config)

        mk_gsi.assert_called_once_with(self.storm.ssh_config)
        mk_gsi.return_value.delete_all_entries.assert_called_once()

        mk_gfm.assert_called_once_with('all entries deleted.', 'success')

    @mock.patch('storm.__main__.get_formatted_message')
    @mock.patch('storm.__main__.get_storm_instance')
    @mock.patch('__builtin__.print')
    def test_delete_all_except(self, mk_print, mk_gsi, mk_gfm):
        mk_gsi.return_value.delete_all_entries.side_effect = Exception("Boom!")

        delete_all(self.storm.ssh_config)

        mk_gsi.assert_called_once_with(self.storm.ssh_config)
        mk_gfm.assert_called_once_with("Boom!", 'error')


if __name__ == '__main__':
    unittest.main()
