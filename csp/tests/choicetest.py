
import unittest
from .. import *


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

        sync(p)

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

        sync(p1, p2)


    def test_iteration(self):
        c1 = Channel()
        c2 = Channel()
        c3 = Channel()

        p1 = spawn(iterate([0], cout=c1))
        p2 = spawn(iterate([1], cout=c2))
        p3 = spawn(iterate([2], cout=c3))

        for (v, i) in enumerate(c1 | c2 | c3):
            self.assertEqual(i, v)

        sync(p1, p2, p3)

    def test_notification(self):
        c1 = Channel()
        c2 = Channel()

        @process
        def reader(cin, cout):
            self.assertEqual(42, select(c1 | c2))
            self.assertEqual(42, select(c1 | c2))

        parallel(reader(), iterate([42], cout=c1), iterate([42], cout=c2))
