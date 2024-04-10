import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import AsyncGenerator, Iterable

from tsk_monster.util import make, need

lg = logging.getLogger(__name__)


@dataclass
class Tsk:
    name: str
    gen: AsyncGenerator

    def __repr__(self):
        return self.name


async def plan(tsks: Iterable[Tsk], n=8):
    async def step(tsk: Tsk):
        lg.info(f'Running {tsk.name}')
        res = await anext(tsk.gen)
        lg.info(f'Finished {tsk.name}')
        return res

    tsks = deque(tsks)
    wait = defaultdict(list)
    done = set()

    while tsks:
        head = [tsks.popleft() for _ in range(min(n, len(tsks)))]

        results = await asyncio.gather(
            *(step(tsk) for tsk in head),
            return_exceptions=True)

        assert len(head) == len(results)

        for tsk, res in zip(head, results):
            if isinstance(res, need) and res.val not in done:
                wait[res.val].append(tsk)

            if isinstance(res, make):
                done.add(res.val)
                for w in wait.pop(res.val, []):
                    tsks.append(w)
                tsks.append(tsk)

            if isinstance(res, Tsk):
                tsks.append(res)
                tsks.append(tsk)

    if wait:
        print(f'Could not run all tasks: {wait}')

    else:
        print('All tasks finished.')

    return wait
