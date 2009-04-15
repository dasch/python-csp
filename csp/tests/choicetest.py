
from testcase import *


class ChoiceTest(TestCase):

    def test_single_choice(self):
        c = Channel()

        @process
        def writer(cin, cout):
            cout << 42
            poison(cout)

        with spawned(writer(cout=c)):
            choice = Choice(c)
            self.assertEqual(42, select(choice))

    def test_multiple_choice(self):
        c1 = Channel()
        c2 = Channel()

        with spawned(iterate([42], cout=c1), iterate([42], cout=c2)):
            self.assertEqual(42, select(c1 | c2))
            self.assertEqual(42, select(c1 | c2))

            try:
                select(c1 | c2)
                self.fail("Should not allow selecting from poisoned choice")
            except ChannelPoisoned:
                self.assert_(True)

    def test_iteration(self):
        c1 = Channel()
        c2 = Channel()
        c3 = Channel()

        channels = [c1, c2, c3]
        processes = [iterate([i], cout=channels[i]) for i in xrange(3)]

        with spawned(*processes):
            for (v, i) in enumerate(c1 | c2 | c3):
                self.assertEqual(i, v)

    def test_notification(self):
        c1 = Channel()
        c2 = Channel()

        @process
        def reader(cin, cout):
            self.assertEqual(42, select(c1 | c2))
            self.assertEqual(42, select(c1 | c2))

        parallel(reader(), iterate([42], cout=c1), iterate([42], cout=c2))

    def test_does_not_discard_messages(self):
        c1 = Channel()
        c2 = Channel()

        @process
        def p1(cout):
            cout << 1

        @process
        def p2(cout):
            cout << 1 << 1

        with spawned(p1(cout=c1), p2(cout=c2)):
            self.assertEqual(1, select(c1 | c2))
            self.assertEqual(1, select(c1 | c2))
            self.assertEqual(1, select(c1 | c2))
