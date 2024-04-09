from collections import defaultdict, deque
from typing import Generator, Iterable

from tsk.util import make, need


def run(tsks: Iterable[Generator]):
    tsks = deque(tsks)
    wait = defaultdict(list)
    done = set()

    while tsks:
        try:
            tsk = tsks.popleft()
            res = next(tsk)

            if isinstance(res, need) and res.val not in done:
                wait[res.val].append(tsk)

            if isinstance(res, make):
                done.add(res.val)
                for w in wait.pop(res.val, []):
                    tsks.append(w)
                tsks.append(tsk)

            if isinstance(res, Generator):
                tsks.append(res)
                tsks.append(tsk)

        except StopIteration:
            pass

    if wait:
        print(f'Could not finish all tasks. {wait}')

    else:
        print('All tasks finished.')

    return wait
