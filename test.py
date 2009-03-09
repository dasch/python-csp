
from csp import *


@process
def source(cin, cout):
    cout << "foo" << "bar" << "baz"
    poison(cout)


@process
def sink(cin, cout):
    for message in cin:
        print message
    poison(cout)


parallel(source() >> map(str.upper) >> sink())
