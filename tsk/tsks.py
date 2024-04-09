import os
from pathlib import Path

from tsk.util import change, pull, push


def shell(cmd, *, deps=[], prods=[]):
    for d in deps:
        yield pull(d)

    os.system(cmd)

    for p in prods:
        yield push(p)


if __name__ == '__main__':
    print(change(Path('tmp.txt')))
    print(change(Path('tmp.txt')))
