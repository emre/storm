from __future__ import unicode_literals

import getpass
import os
import shlex
import subprocess

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import six

from storm import Storm
from storm.parsers.ssh_uri_parser import parse
from storm import __version__


# derived from http://www.cyberciti.biz/faq/create-ssh-config-file-on-linux-unix/
FAKE_SSH_CONFIG_FOR_CLI_TESTS = """
    ### default for all ##
    Host *
         ForwardAgent no
         ForwardX11 no
         ForwardX11Trusted yes
         User nixcraft
         Port 22
         Protocol 2
         ServerAliveInterval 60
         ServerAliveCountMax 30
         LocalForward 3128 127.0.0.1:3128
         LocalForward 3129 127.0.0.1:3128

    ## override as per host ##
    Host server1
         HostName server1.cyberciti.biz
         User nixcraft
         Port 4242
         IdentityFile /nfs/shared/users/nixcraft/keys/server1/id_rsa
         IdentityFile /tmp/x.rsa

    ## Home nas server ##
    Host nas01
         HostName 192.168.1.100
         User root
         IdentityFile ~/.ssh/nas01.key

    ## Login AWS Cloud ##
    Host aws.apache
         HostName 1.2.3.4
         User wwwdata
         IdentityFile ~/.ssh/aws.apache.key

    ## Login to internal lan server at 192.168.0.251 via our public uk office ssh based gateway using ##
    ## $ ssh uk.gw.lan ##
    Host uk.gw.lan uk.lan
         HostName 192.168.0.251
         User nixcraft
         ProxyCommand  ssh nixcraft@gateway.uk.cyberciti.biz nc %h %p 2> /dev/null

    ## Our Us Proxy Server ##
    ## Forward all local port 3128 traffic to port 3128 on the remote vps1.cyberciti.biz server ##
    ## $ ssh -f -N  proxyus ##
    Host proxyus
        HostName vps1.cyberciti.biz
        User breakfree
        IdentityFile ~/.ssh/vps1.cyberciti.biz.key
        LocalForward 3128 127.0.0.1:3128
"""


class StormCliTestCase(unittest.TestCase):

    def setUp(self):
        self.config_file = '/tmp/ssh_config_cli_tests'
        with open(self.config_file, 'w+') as f:
            f.write(FAKE_SSH_CONFIG_FOR_CLI_TESTS)

        self.config_arg = '--config={0}'.format(self.config_file)

    def run_cmd(self, cmd):

        cmd = 'storm %s' % cmd
        cmd = shlex.split(cmd.encode('utf-8') if six.PY2 else cmd)
        _env = os.environ
        _env["TESTMODE"] = "1"

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   env=_env)
        out, err = process.communicate()
        rc = process.returncode
        return out, err, rc

    def test_list_command(self):
        out, err, rc = self.run_cmd('list {0}'.format(self.config_arg))

        self.assertTrue(out.startswith(b" Listing entries:\n\n"))

        hosts, custom_options = [
            "aws.apache -> wwwdata@1.2.3.4:22",
            "nas01 -> root@192.168.1.100:22",
            "proxyus -> breakfree@vps1.cyberciti.biz:22",
            "server1 -> nixcraft@server1.cyberciti.biz:4242",
            "uk.gw.lan uk.lan -> nixcraft@192.168.0.251:22",
        ], [
            "[custom options] identityfile=~/.ssh/aws.apache.key",
            "[custom options] identityfile=~/.ssh/nas01.key",
            "identityfile=~/.ssh/vps1.cyberciti.biz.key",
            "localforward=3128 127.0.0.1:3128",
            "[custom options] identityfile=/nfs/shared/users/nixcraft/keys/server1/id_rsa,/tmp/x.rsa",
            "[custom options] proxycommand=ssh nixcraft@gateway.uk.cyberciti.biz nc %h %p 2> /dev/null",
        ]

        general_options = {
            "forwardx11": "no",
            "protocol": "2",
            "user": "nixcraft",
            "forwardagent": "no",
            "forwardx11trusted": "yes",
            "serveralivecountmax": "30",
            "serveraliveinterval": "60",
            "port": "22",
            "localforward": "3128 127.0.0.1:3128, 3129 127.0.0.1:3128",
        }

        for host in hosts:
            self.assertIn(host.encode('ascii'), out)

        for custom_option in custom_options:
            self.assertIn(custom_option.encode('ascii'), out)

        for general_option, value in six.iteritems(general_options):
            self.assertIn("{0}: {1}".format(general_option, value).encode('ascii'), out)

        self.assertEqual(err, b'')
        self.assertEqual(rc, 0)

    def test_version_command(self):
        out, err, rc = self.run_cmd('version')
        self.assertIn(__version__.encode('ascii'), out)

    def test_basic_add(self):
        out, err, rc = self.run_cmd('add netscaler ns@42.42.42.42 {0}'.format(self.config_arg))

        self.assertIn(b"success", out)

    def test_add_duplicate(self):
        out, err, rc = self.run_cmd('add aws.apache test@test.com {0}'.format(self.config_arg))

        self.assertEqual(b'', out)
        self.assertIn(b'error', err)

    def test_add_invalid_host(self):
        out, err, rc = self.run_cmd('add @_@ test.com {0}'.format(self.config_arg))

        self.assertEqual(b'', out)
        self.assertIn(b'error', err)

    def test_advanced_add(self):
        out, err, rc = self.run_cmd('add postgresql-server postgres@192.168.1.1 {0} {1}{2}'.format(
            "--id_file=/tmp/idfilecheck.rsa ",
            '--o "StrictHostKeyChecking=yes" --o "UserKnownHostsFile=/dev/advanced_test" ',
            self.config_arg)
        )

        self.assertIn(b"success", out)

        with open(self.config_file) as f:
            # check that property is really flushed out to the config?
            content = f.read().encode('ascii')
            self.assertIn(b'identityfile "/tmp/idfilecheck.rsa"', content)
            self.assertIn(b"stricthostkeychecking yes", content)
            self.assertIn(b"userknownhostsfile /dev/advanced_test", content)

    def test_add_with_idfile(self):
        out, err, rc = self.run_cmd('add postgresql-server postgres@192.168.1.1 {0} {1}'.format(
            "--id_file=/tmp/idfileonlycheck.rsa",
            self.config_arg)
        )

        self.assertIn(b"success", out)

        with open(self.config_file) as f:
            content = f.read().encode('ascii')
            self.assertIn(b'identityfile "/tmp/idfileonlycheck.rsa"', content)

    def test_basic_edit(self):
        out, err, rc = self.run_cmd('edit aws.apache basic_edit_check@10.20.30.40 {0}'.format(self.config_arg))

        self.assertIn(b"success", out)

        with open(self.config_file) as f:
            content = f.read().encode('ascii')
            self.assertIn(b"basic_edit_check", content)
            self.assertIn(b"10.20.30.40", content)

    def test_edit_invalid_host(self):
        out, err, rc = self.run_cmd('edit @missing_host test.com {0}'.format(self.config_arg))

        self.assertEqual(b'', out)
        self.assertIn(b'error', err)

    def test_edit_missing_host(self):
        out, err, rc = self.run_cmd('edit missing_host test.com {0}'.format(self.config_arg))

        self.assertEqual(b'', out)
        self.assertIn(b'error', err)

    def test_update(self):
        out, err, rc = self.run_cmd('update aws.apache --o "user=daghan" --o port=42000 {0}'.format(self.config_arg))

        self.assertIn(b"success", out)

        with open(self.config_file) as f:
            content = f.read().encode('ascii')
            self.assertIn(b"user daghan", content)  # see daghan: http://instagram.com/p/lfPMW_qVja
            self.assertIn(b"port 42000", content)

    def test_update_regex(self):

        self.run_cmd('add worker alphaworker.com {0}'.format(self.config_arg))

        # add three machines -- hostnames starts with worker-N
        self.run_cmd('add worker-1 worker1.com {0}'.format(self.config_arg))
        self.run_cmd('add worker-2 worker2.com {0}'.format(self.config_arg))
        self.run_cmd('add worker-4 worker4.com {0}'.format(self.config_arg))

        # another one -- regex shouldn't capture that one though.
        self.run_cmd('add worker3 worker3.com {0}'.format(self.config_arg))

        out, err, rc = self.run_cmd("update 'worker-[1-5]' --o hostname=boss.com {0}".format(self.config_arg))

        self.assertIn(b"success", out)

        # edit the alphaworker
        out, err, rc = self.run_cmd('edit worker alphauser@alphaworker.com {0}'.format(self.config_arg))

        with open(self.config_file) as f:
            content = f.read().encode('ascii')
            self.assertNotIn(b"worker1.com", content)
            self.assertNotIn(b"worker2.com", content)
            self.assertNotIn(b"worker4.com", content)
            self.assertIn(b"worker3.com", content)
            self.assertIn(b"alphauser", content)

        out, err, rc = self.run_cmd("edit worker  {0}".format(self.config_arg))

    def test_update_invalid_regex(self):

        out, err, rc = self.run_cmd("update 'drogba-[0-5]' --o hostname=boss.com {0}".format(self.config_arg))

        self.assertEqual(b'', out)
        self.assertIn(b'error', err)

    def test_delete(self):
        out, err, rc = self.run_cmd("delete server1 {0}".format(self.config_arg))
        self.assertIn(b"success", out)

    def test_delete_invalid_hostname(self):

        out, err, rc = self.run_cmd("delete unknown_server".format(self.config_arg))

        self.assertEqual(b'', out)
        self.assertIn(b'error', err)

    def test_search(self):

        out, err, rc = self.run_cmd("search aws {0}".format(self.config_arg))

        self.assertTrue(out.startswith(b'Listing results for aws:'))
        self.assertIn(b'aws.apache', out)

    def test_backup(self):
        out, err, rc = self.run_cmd("backup /tmp/ssh_backup {0}".format(
            self.config_arg))

        self.assertEqual(True, os.path.exists("/tmp/ssh_backup"))

    def test_invalid_search(self):

        out, err, rc = self.run_cmd("search THEREISNOTHINGRELATEDWITHME {0}".format(self.config_arg))

        self.assertIn(b'no results found.', out)

    def test_delete_all(self):
        out, err, rc = self.run_cmd('delete_all {0}'.format(self.config_arg))

        self.assertIn(b'all entries deleted', out)

    def tearDown(self):
        os.unlink('/tmp/ssh_config_cli_tests')


class StormTests(unittest.TestCase):

    def setUp(self):
        fake_ssh_config = """Host *
            IdentitiesOnly yes

        Host netscaler
            hostname 1.1.1.1
            port 3367

        """

        with open('/tmp/ssh_config', 'w+') as f:
            f.write(fake_ssh_config)

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
                self.assertEqual(item.get("options").get("identityfile"), '"/tmp/tmp.pub"')

    def test_clone_host(self):
        self.storm.add_entry('google', 'google.com', 'ops', '24', '/tmp/tmp.pub')
        self.storm.clone_entry('google', 'yahoo')

        has_yahoo = False
        for item in self.storm.ssh_config.config_data:
            if item.get("host") == 'yahoo': 
                has_yahoo = True
                break

        self.assertEqual(True, has_yahoo) 
        self.assertEqual(item.get("options").get("port"), '24')
        self.assertEqual(item.get("options").get("identityfile"), '"/tmp/tmp.pub"')
        self.assertEqual(item.get("options").get("user"), 'ops')

    def test_move_host(self):
        self.storm.add_entry('google', 'google.com', 'ops', '24', '/tmp/tmp.pub')
        self.storm.clone_entry('google', 'yahoo', keep_original=False)

        has_yahoo = False
        for item in self.storm.ssh_config.config_data:
            if item.get("host") == 'yahoo':
                has_yahoo = True
                break

        has_google = False
        for item in self.storm.ssh_config.config_data:
            if item.get("host") == 'google':
                has_google = True
                break

        self.assertEqual(True, has_yahoo)
        self.assertEqual(False, has_google)
        self.assertEqual(item.get("options").get("port"), '24')
        self.assertEqual(item.get("options").get("identityfile"), '"/tmp/tmp.pub"')
        self.assertEqual(item.get("options").get("user"), 'ops')

    def test_backup(self):
        self.storm.backup("/tmp/storm_ssh_config_backup_file")
        self.assertEqual(
            True,
            os.path.exists("/tmp/storm_ssh_config_backup_file")
        )

    def test_double_clone_exception(self):
        self.storm.add_entry('google', 'google.com', 'ops', '24', '/tmp/tmp.pub')
        self.storm.clone_entry('google', 'yahoo')

        with self.assertRaises(ValueError):
            self.storm.clone_entry('google', 'yahoo')

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
        self.assertRaises(ValueError, parse, 'root@emreyilmaz.me:string-port')

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
                self.assertEqual(item.get("options").get("stricthostkeychecking"), 'no')
                self.assertEqual(item.get("options").get("userknownhostsfile"), '/dev/null')

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
                self.assertEqual(item.get("options").get("stricthostkeychecking"), 'yes')
                self.assertEqual(item.get("options").get("userknownhostsfile"), '/home/emre/foo')

    def tearDown(self):
        os.unlink('/tmp/ssh_config')

if __name__ == '__main__':
    unittest.main()
