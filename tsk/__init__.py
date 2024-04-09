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

    return wait
