
from testcase import *


class ChannelTest(TestCase):

    def test_can_transmit_message(self):
        c = Channel()

        @process
        def p(cin, cout):
            cout << 42

        with spawned(p(cout=c)):
            self.assertEqual(42, read(c))

    def test_can_write_none(self):
        c = Channel()

        @process
        def p1(cin, cout):
            cout << None

        with spawned(p1(cout=c)):
            self.assertEqual(None, read(c))

    def test_should_block_on_write(self):
        @process
        def writer(cout):
            cout << 42
            self.fail("Expected to block on writes")

        p = spawn(writer())
