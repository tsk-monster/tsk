from collections import defaultdict, deque
from typing import Generator, Iterable

from tsk.util import make, need

Tsk = Generator[need | make | 'Tsk', None, None]


def run(tsks: Iterable[Tsk]):
    tsks = deque(tsks)
    wait = defaultdict(list)
    done = set()

    while tsks:
        try:
            tsk = tsks.popleft()
            res = next(tsk)

            if isinstance(res, need) and res.val not in done:
                wait[res.val].append(tsk)

            elif isinstance(res, make):
                done.add(make.val)
                for w in wait.pop(make.val, []):
                    tsks.append(w)
                tsks.append(tsk)

            elif isinstance(res, Generator):
                tsks.append(res)
                tsks.append(tsk)

            else:
                raise ValueError('Invalid tsk result.')

        except StopIteration:
            pass

    if wait:
        print('Could not finish all tasks.')

    else:
        print('All tasks finished.')

    return wait
