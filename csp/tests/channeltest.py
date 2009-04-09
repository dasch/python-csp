
import unittest
from .. import *


class ChannelTest(unittest.TestCase):

    def test_can_write_none(self):
        c = Channel()

        @process
        def p1(cin, cout):
            cout << None

        p = spawn(p1(cout=c))

        self.assertEqual(None, read(c))

        sync(p)
