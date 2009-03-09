
from time import sleep

from csp import *


@process
def source(cin, cout):
    cout << "foo" << "bar" << "baz" << "bum"
    poison(cout)


@process
def sink(cin, cout, name):
    print "[%s] starting..." % name
    for message in cin:
        print "[%s] received: %s" % (name, message)
        sleep(1)
    print "[%s] terminating..." % name
    poison(cout)


p1 = source()
p2 = p1 >> sink("A")
p3 = p1 >> sink("B")

parallel(p1, p2, p3)
