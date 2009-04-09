
from testcase import *


class UtilsTest(TestCase):

    def test_iterate(self):
        c = Channel()

        it = spawn(iterate([1, 2, 3], cout=c))

        self.assertEqual(1, read(c))
        self.assertEqual(2, read(c))
        self.assertEqual(3, read(c))

        sync(it)
