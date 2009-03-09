
from time import sleep

from csp import *


@process
def source(cin, cout):
    cout << "foo" << "bar" << "baz" << "bum"


@process
def sink(cin, cout, name):
    cout << "[%s] starting..." % name
    for message in cin:
        cout << "[%s] received: %s" % (name, message)
        sleep(0.5)
    cout << "[%s] terminating..." % name


@process
def printer(cin, cout):
    for message in cin:
        print message


parallel(source() >> (sink("A") + sink("B")) >> printer())
