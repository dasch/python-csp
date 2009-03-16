
from itertools import ifilter

from csp.core import *


def pool(processes):
    @process
    def _pool(cin, cout):
        parallel(*[p(cin=cin, cout=cout) for p in processes])
        poison(cout)

    return _pool

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
