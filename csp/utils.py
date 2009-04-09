
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


@process
def iterate(seq, cout):
    """Write each value in seq to cout."""
    for value in seq:
        cout << value
    poison(cout)
