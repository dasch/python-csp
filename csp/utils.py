
from itertools import ifilter

from csp.core import *


def map(func):
    @process
    def _map(cin, cout):
        for message in cin:
            cout << func(message)
        poison(cout)

    return _map()


def filter(predicate=None):
    @process
    def _filter(cin, cout):
        for message in ifilter(predicate, cin):
            cout << message
        poison(cout)

    return _filter()


def iterator(seq):
    @process
    def _iterator(cin, cout):
        for value in seq:
            cout << value
        poison(cout)

    return _iterator
