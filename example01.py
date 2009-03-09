
from time import sleep

from csp import *


@process
def source(cin, cout):
    for message in ["foo", "bar", "baz"]:
        cout << message << "butt"
        sleep(0.5)
    poison(cout)


@process
def sink(cin, cout):
    for message in cin:
        print message
    poison(cout)


parallel(source() >> filter(lambda m: m != "butt") >> map(str.upper) >> sink())
