
from testcase import *


class ProcessTest(TestCase):

    def test_process_with_no_channels(self):
        try:
            @process
            def p():
                self.assert_(True)

            parallel(p())
        except TypeError:
            self.flunk()
