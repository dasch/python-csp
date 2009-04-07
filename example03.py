
from csp import *


@process
def writer(cin, cout, value):
    cout << value
    poison(cout)


c1 = Channel()
c2 = Channel()

p1 = spawn(writer(42, cout=c1))
p2 = spawn(writer(19, cout=c2))

sync(p1)
sync(p2)

print select(c1 | c2)
print select(c1 | c2)
