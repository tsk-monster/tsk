import os
from collections import defaultdict, deque
from typing import Any, Generator, Iterable, Tuple

tsk = Generator[Tuple[bool, Any], None, None]


def run(tsks: Iterable[tsk]):
    tsks = deque(tsks)
    wait = defaultdict(list)
    done = set()

    while tsks:
        try:
            tsk = tsks.popleft()
            need, val = next(tsk)
            if need and val not in done:
                wait[val].append(tsk)
            else:
                done.add(val)
                for w in wait.pop(val, []):
                    tsks.append(w)
                tsks.append(tsk)
        except StopIteration:
            pass

    if wait:
        print('Could not finish all tasks.')
    else:
        print('All tasks finished.')


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


if __name__ == '__main__':
    print()
    print('start')

    run([
        shell('echo "need a prod b"', deps=['a'], prods=['b']),
        shell('echo "prod a"', prods=['a']),
    ])
