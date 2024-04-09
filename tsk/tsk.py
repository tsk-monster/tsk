from collections import defaultdict, deque
from typing import Any, Generator, Tuple

tsk = Generator[Tuple[bool, Any], None, None]


def run(tsks: deque[tsk]):
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


if __name__ == '__main__':
    print()
    print('start')

    def tsk1():
        yield push('tsk1')
        yield pull('tsk1')
        print('tsk1')

    def tsk2():
        yield push('tsk2')
        yield pull('tsk2')
        print('tsk2')

    run(deque([tsk1(), tsk2()]))
