
from csp import *


@process
def source(cin, cout):
    cout << "foo" << "bar" << "baz"
    poison(cout)


@process
def sink(cin, cout, name):
    for message in cin:
        print "[%s] %s" % (name, message)


p1 = source()
p2 = p1 >> sink("A")
p3 = p1 >> sink("B")

parallel(p1, p2, p3)
