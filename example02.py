
from time import sleep

from csp import *


@process
def source(cin, cout):
    cout << "foo" << "bar" << "baz" << "bum"
    poison(cout)


@process
def sink(cin, cout, name):
    cout << "[%s] starting..." % name
    for message in cin:
        cout << "[%s] received: %s" % (name, message)
        sleep(0.5)
    cout << "[%s] terminating..." % name
    poison(cout)


@process
def printer(cin, cout):
    for message in cin:
        print message
    poison(cout)


parallel(source() >> (sink("A") + sink("B")) >> printer())
