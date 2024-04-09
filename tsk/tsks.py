import os
from pathlib import Path


def pull(val):
    return (True, val)


def push(val):
    return (False, val)


def change(path: Path):
    try:
        tsk = path.with_suffix('.tsk')
        if not tsk.exists():
            return True

        return tsk.stat().st_mtime < path.stat().st_mtime
    finally:
        tsk.touch()


def shell(cmd, *, deps=[], prods=[]):
    for d in deps:
        yield pull(d)

    os.system(cmd)

    for p in prods:
        yield push(p)


if __name__ == '__main__':
    print(change(Path('tmp.txt')))
    print(change(Path('tmp.txt')))
