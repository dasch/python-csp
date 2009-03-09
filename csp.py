
from threading import Thread, Condition
from functools import wraps


class ChannelPoisoned(Exception): pass


class Process:
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

        if "cin" not in kwargs:
            kwargs["cin"] = Channel()

        if "cout" not in kwargs:
            kwargs["cout"] = Channel()

        self._cin = kwargs["cin"]
        self._cout = kwargs["cout"]

        def runner():
            func(*args, **kwargs)

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


def current_process():
    return Thread.current_thread()._process


def send(message, channel=None):
    """Send a message to cout or channel."""
    if channel is None:
        channel = current_process()._cout

    channel._write(message)


def receive(channel=None):
    """Read a message from cout or channel."""
    if channel is None:
        channel = current_process()._cout

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


def cin():
    return current_process()._cin


def cout():
    return current_process()._cout


def pipe(p1, p2):
    @process
    def _pipe(cin, cout):
        cin = p1._cout
        cout = p2._cin
        for message in cin:
            send(message, cout)
    return _pipe


def pipeline(*processes):
    i = iter(processes)
    p1 = i.next
    ps = []

    for p2 in i:
        ps.append(pipe(p1, p2))
        p1 = p2

    @process
    def _pipeline(cin, cout):
        parallel(*[p() for p in ps])

    return _pipeline
