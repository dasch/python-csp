
from __future__ import with_statement
from threading import Thread, Condition
from functools import wraps


class ChannelPoisoned(Exception): pass


class Process:
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._running = False

        self._cin = kwargs.pop("cin", Channel())
        self._cout = kwargs.pop("cout", Channel())

        def runner():
            func(self._cin, self._cout, *args, **kwargs)

        self._thread = Thread(target=runner)

    def _start(self):
        if not self._running:
            self._running = True
            self._thread.start()

    def _join(self):
        self._thread.join()

    def __rshift__(self, other):
        """Pipe cout to another process' cin."""
        return pipe(self, other)

    def __add__(self, other):
        return combine(self, other)


class Channel:

    def __init__(self):
        self._value = None
        self._poisoned = False
        self._cond = Condition()

    def _read(self):
        try:
            self._cond.acquire()
            while self._value is None:
                if self._poisoned: raise ChannelPoisoned()
                self._cond.wait()
            return self._value
        finally:
            self._value = None
            self._cond.notify()
            self._cond.release()

    def _write(self, value):
        with self._cond:
            while self._value is not None:
                if self._poisoned: raise ChannelPoisoned()
                self._cond.wait()
            self._value = value
            self._cond.notify()

    def _poison(self):
        self._cond.acquire()
        self._poisoned = True
        self._cond.notify()
        self._cond.release()

    def __lshift__(self, value):
        """Write a value to the channel."""
        self._write(value)
        return self

    def __iter__(self):
        try:
            while True: yield self._read()
        except ChannelPoisoned:
            pass


def process(func):
    """Turn a function into a process definition."""
    @wraps(func)
    def _process(*args, **kwargs):
        return Process(func, *args, **kwargs)
    return _process


def send(message, channel):
    """Send a message to a channel."""
    channel._write(message)


def receive(channel):
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


@process
def copy(cin, cout):
    """Copy all messages sent to cin to cout.

    When cin is poisoned, the poison is transferred to cout.
    """
    for message in cin:
        cout << message
    poison(cout)


@process
def combine(cin, cout, *processes):
    @process
    def forward(cin, cout):
        for message in cin:
            cout << message

    def _copiers():
        for p in processes:
            yield copy(cin=cin, cout=p._cin)
            yield forward(cin=p._cout, cout=cout)
            yield p

    parallel(*_copiers())
    poison(cout)


def pipe(p1, p2):
    @process
    def _pipe(cin, cout):
        parallel(copy(cin=p1._cout, cout=p2._cin),
                 copy(cin=p2._cout, cout=cout),
                 p1, p2)

    return _pipe()
