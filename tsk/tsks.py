import os


def pull(val):
    return (True, val)


def push(val):
    return (False, val)


def shell(cmd, *, deps=[], prods=[]):
    for d in deps:
        yield pull(d)

    os.system(cmd)

    for p in prods:
        yield push(p)
