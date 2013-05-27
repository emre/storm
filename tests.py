import unittest
import os

from storm import Storm


class StormTests(unittest.TestCase):

    def setUp(self):
        FAKE_SSH_CONFIG = """Host *
            IdentitiesOnly yes

        Host netscaler
            hostname 1.1.1.1
            port 3367

        """

        f = open('/tmp/ssh_config', 'w+')
        f.write(FAKE_SSH_CONFIG)
        f.close()

        self.storm = Storm('/tmp/ssh_config')

    def test_config_load(self):
        self.assertEqual(self.storm.ssh_config.config_data[1]["options"]["identitiesonly"], 'yes')

    def test_config_dump(self):
        self.storm.ssh_config.write_to_ssh_config()

        for search_str in ["hostname 1.1.1.1", "Host netscaler", "Host *"]:
            self.assertEqual(True, search_str in open('/tmp/ssh_config').read())

    def test_update_host(self):
        self.storm.ssh_config.update_host("netscaler", {"hostname": "2.2.2.2"})
        self.assertEqual(self.storm.ssh_config.config_data[4]["options"]["hostname"], '2.2.2.2')

    def test_add_host(self):
        self.storm.add_entry('google', 'google.com', 'root', '22', '/tmp/tmp.pub')
        self.storm.ssh_config.write_to_ssh_config()

        for item in self.storm.ssh_config.config_data:
            if item.get("host") == 'google':
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

    def test_delete_host(self):
        self.storm.delete_entry('netscaler')
        for host in self.storm.ssh_config.config_data:
            self.assertEqual(False, host.get("host") == 'netscaler')

    def test99_delete_all(self):
        self.storm.delete_all_entries()
        self.assertEqual(len(self.storm.ssh_config.config_data), 0)

    def tearDown(self):
        os.unlink('/tmp/ssh_config')

if __name__ == '__main__':
    unittest.main()