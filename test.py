
from csp import *


@process
def source(cin, cout):
    cout << "foo" << "bar" << "baz"
    poison(cout)


@process
def upcase(cin, cout):
    for message in cin:
        cout << message.upper()
    poison(cout)


@process
def sink(cin, cout):
    for message in cin:
        print message
    poison(cout)


parallel(source() >> upcase() >> sink())
