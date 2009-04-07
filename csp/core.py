
from __future__ import with_statement
import threading
import functools


_NULL = object()

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

        self._thread = threading.Thread(target=runner)

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
        self._value = _NULL
        self._poisoned = False
        self._listeners = []
        self._cond = threading.Condition()

    def _read(self):
        try:
            self._cond.acquire()
            while self._value is _NULL:
                if self._poisoned: raise ChannelPoisoned()
                self._cond.wait()
            return self._value
        finally:
            self._value = _NULL
            self._cond.notify()
            self._cond.release()

    def _select(self, choice):
        with self._cond:
            if self._value is not _NULL:
                value = self._value
                self._value = _NULL
                return value
            elif self._poisoned:
                raise ChannelPoisoned()
            else:
                self._listeners.append(choice)
                return _NULL

    def _write(self, value):
        with self._cond:
            while self._value is not _NULL:
                if self._poisoned: raise ChannelPoisoned()
                self._cond.wait()

            if self._listeners:
                listener = self._listeners.pop()
                if listener._put(value):
                    return

            self._value = value
            self._cond.notify()

    def _poison(self):
        with self._cond:
            self._poisoned = True
            self._cond.notify()

    def __lshift__(self, value):
        """Write a value to the channel."""
        self._write(value)
        return self

    def __iter__(self):
        try:
            while True: yield self._read()
        except ChannelPoisoned:
            pass

    def __or__(self, other):
        return Choice(self, other)


class Choice:

    def __init__(self, *guards):
        self._guards = list(guards)
        self._cond = threading.Condition()

    def _select(self):
        self._value = _NULL

        with self._cond:
            num_poisoned = 0

            for guard in self._guards:
                try:
                    value = guard._select(self)

                    if value is not _NULL:
                        return value
                except ChannelPoisoned:
                    num_poisoned += 1

            if num_poisoned == len(self._guards):
                raise ChannelPoisoned()

            while self._value is _NULL:
                self._cond.wait()

            value = self._value
            self._value = _NULL

            return value

    def _put(self, value):
        with self._cond:
            if self._value is _NULL:
                self._value = value

    def __or__(self, other):
        self._guards.append(other)
        return self

    def __iter__(self):
        try:
            while True:
                yield self._select()
        except ChannelPoisoned:
            pass




def process(func):
    """Turn a function into a process definition."""
    @functools.wraps(func)
    def _process(*args, **kwargs):
        return Process(func, *args, **kwargs)
    return _process


def write(message, channel):
    """Send a message to a channel."""
    channel._write(message)


def read(channel):
    """Read a message from a channel."""
    return channel._read()


def select(choice):
    """Read a message from a choice of sources.
    
    The sources include channels, skips, and timeouts."""
    return choice._select()

def poison(channel):
    """Poison a channel."""
    channel._poison()


def spawn(p):
    """Start processes."""
    p._start()
    return p


def sync(*processes):
    """Wait for processes to finish."""
    for p in processes:
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
