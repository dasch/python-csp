
import unittest

from csp import *


class ChannelTest(unittest.TestCase):

    def test_can_write_none(self):
        c = Channel()

        @process
        def p1(cin, cout):
            cout << None

        p = spawn(p1(cout=c))

        self.assertEqual(None, read(c))


class UtilsTest(unittest.TestCase):

    def test_iterate(self):
        c = Channel()

        it = spawn(iterate([1, 2, 3], cout=c))

        self.assertEqual(1, read(c))
        self.assertEqual(2, read(c))
        self.assertEqual(3, read(c))


class ChoiceTest(unittest.TestCase):

    def test_single_choice(self):
        c = Channel()

        @process
        def writer(cin, cout):
            cout << 42
            poison(cout)

        p = spawn(writer(cout=c))

        choice = Choice(c)

        self.assertEqual(42, select(choice))

    def test_multiple_choice(self):
        c1 = Channel()
        c2 = Channel()

        p1 = spawn(iterate([42], cout=c1))
        p2 = spawn(iterate([42], cout=c2))

        self.assertEqual(42, select(c1 | c2))
        self.assertEqual(42, select(c1 | c2))

        try:
            select(c1 | c2)
            self.fail("Should not allow selecting from poisoned choice")
        except ChannelPoisoned:
            self.assert_(True)


if __name__ == "__main__":
    unittest.main()
