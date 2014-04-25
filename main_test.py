import unittest
import mock

from storm import Storm

# Monkey patch get_formatted_message so it does not print anything when tests are run
import storm.__main__ as s
s.get_formatted_message = mock.MagicMock()
s.get_formatted_message.return_value = ""

class StormMainTest(unittest.TestCase):
    def test_udpate(self): 
        Storm.update_entry = mock.MagicMock()
        s.update("google")
        Storm.update_entry.assert_called_with("google")

if __name__ == '__main__':
    unittest.main()
