
from time import sleep

from csp import *


@process
def source(cin, cout):
    for message in ["foo", "bar", "baz"]:
        cout << message << "butt"
        sleep(1)
    poison(cout)


@process
def sink(cin, cout):
    for message in cin:
        print message
    poison(cout)

parallel(source() >> map(str.upper) >> sink())
