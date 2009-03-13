
import unittest

from csp import *

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
