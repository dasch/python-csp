
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

    def test_iterator(self):
        c = Channel()
        it = iterator([1, 2, 3])

        p = spawn(it(cout=c))

        self.assertEqual(1, read(c))
        self.assertEqual(2, read(c))
        self.assertEqual(3, read(c))

        sync(p)


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

        @process
        def writer(cin, cout, seq):
            for value in seq:
                cout << value
            poison(cout)

        p1 = spawn(writer([42], cout=c1))
        p2 = spawn(writer([42], cout=c2))

        self.assertEqual(42, select(c1 | c2))
        self.assertEqual(42, select(c1 | c2))

        try:
            select(c1 | c2)
            self.fail("Should not allow selecting from poisoned choice")
        except ChannelPoisoned:
            self.assert_(True)


if __name__ == "__main__":
    unittest.main()
