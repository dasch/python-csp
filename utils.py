

def pairwise(seq):
    it = iter(seq)
    p1 = it.next()

    for p2 in it:
        yield (p1, p2)
        p1 = p2
