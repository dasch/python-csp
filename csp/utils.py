
from itertools import ifilter
from contextlib import contextmanager

from csp.core import *


@contextmanager
def spawned(*processes):
    """Run a block concurrently with the specified processes.
    
    The processes will be spawned before entering the block and synchronized
    afterwards.
    """
    for process in processes:
        spawn(process)

    # Run the block.
    yield

    for process in processes:
        sync(process)


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


@process
def iterate(cin, cout, seq):
    for value in seq:
        cout << value
    poison(cout)
