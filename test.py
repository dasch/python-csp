
import unittest

from csp import *


class ChannelTest(unittest.TestCase):

    def test_can_send_none(self):
        c = Channel()

        @process
        def p1(cin, cout):
            cout << None

        p = spawn(p1(cout=c))

        self.assertEqual(None, receive(c))


class UtilsTest(unittest.TestCase):

    def test_iterator(self):
        c = Channel()
        it = iterator([1, 2, 3])

        p = spawn(it(cout=c))

        self.assertEqual(1, receive(c))
        self.assertEqual(2, receive(c))
        self.assertEqual(3, receive(c))

        sync(p)


if __name__ == "__main__":
    unittest.main()
