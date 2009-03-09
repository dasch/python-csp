
from threading import Thread, Condition
from functools import wraps
from itertools import chain

from utils import *


class ChannelPoisoned(Exception): pass


class Process:
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

        self._cin = kwargs.pop("cin", Channel())
        self._cout = kwargs.pop("cout", Channel())

        def runner():
            func(self._cin, self._cout, *args, **kwargs)

        self._thread = Thread(target=runner)

    def _start(self):
        self._thread.start()

    def _join(self):
        self._thread.join()


class Channel:

    def __init__(self):
        self._value = None
        self._poisoned = False
        self._cv = Condition()

    def _read(self):
        try:
            self._cv.acquire()
            while self._value is None:
                if self._poisoned: raise ChannelPoisoned()
                self._cv.wait()
            return self._value
        finally:
            self._value = None
            self._cv.notify()
            self._cv.release()

    def _write(self, value):
        try:
            self._cv.acquire()
            while self._value is not None:
                if self._poisoned: raise ChannelPoisoned()
                self._cv.wait()
            self._value = value
            self._cv.notify()
        finally:
            self._cv.release()

    def __lshift__(self, value):
        self._write(value)
        return self

    def _poison(self):
        self._cv.acquire()
        self._poisoned = True
        self._cv.notify()
        self._cv.release()

    def __iter__(self):
        try:
            while True: yield self._read()
        except ChannelPoisoned:
            pass


def process(func):
    @wraps(func)
    def _process(*args, **kwargs):
        return Process(func, *args, **kwargs)
    return _process


def send(message, channel=None):
    """Send a message to a channel."""
    channel._write(message)


def receive(channel=None):
    """Read a message from a channel."""
    return channel._read()


def poison(channel):
    """Poison a channel."""
    channel._poison()


def spawn(p):
    """Start process p."""
    p._start()


def sync(p):
    """Wait for process p to finish."""
    p._join()


def parallel(*processes):
    """Execute the processes in parallel."""
    for p in processes:
        spawn(p)

    for p in processes:
        sync(p)


def sequential(*processes):
    """Execute the processes sequentially."""
    for p in processes:
        spawn(p)
        sync(p)


def pipe(p1, p2):
    @process
    def _pipe(cin, cout):
        @process
        def __pipe(cin, cout):
            for message in cin:
                cout << message
            poison(cout)

        spawn(__pipe(cin=p1._cout, cout=p2._cin))

    return _pipe


def pipeline(*processes):
    pipes = [pipe(p1, p2) for (p1, p2) in pairwise(processes)]

    @process
    def _pipeline(cin, cout):
        parallel(*chain([p() for p in pipes], processes))

    return _pipeline
