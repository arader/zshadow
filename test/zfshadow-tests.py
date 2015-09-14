import unittest
import utils

class TestCommandLine(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_help(self):
        utils.exec_zfshadow()
        pass

if __name__ == '__main__':
    unittest.main()
