import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncGenerator, Awaitable, Callable, Iterable, List

lg = logging.getLogger('👾')


@dataclass
class Need:
    val: Any


@dataclass
class Make:
    val: Any


def changed(path: str | Path):
    try:
        path = Path(path)
        tsk = path.with_suffix('.tsk')
        if not tsk.exists():
            return True

        return tsk.stat().st_mtime < path.stat().st_mtime
    finally:
        tsk.touch()


def none(items: Iterable[bool]):
    return not any(items)


@dataclass
class Tsk:
    name: str
    gen: AsyncGenerator

    def __repr__(self):
        return self.name


def tsk(
        name: str, action: Callable[[], Awaitable], *,
        need: List[Path] = [],
        make: List[Path] = []):

    async def gen():
        always_run = len(need) == len(make) == 0

        for n in need:
            yield Need(n)

        if any(map(changed, need)) or not all(map(Path.exists, make)) or always_run:
            await action()

        for m in make:
            if m.exists():
                yield Make(m)
            else:
                lg.warning(f'Failed to make {m}.')

    return Tsk(name, gen())


def shell(
        cmd: str, *,
        need: List[Path] = [],
        make: List[Path] = []):

    return tsk(
        cmd, lambda: asyncio.create_subprocess_shell(cmd),
        need=need,
        make=make)


async def plan(tsks: Iterable[Tsk], parallelism=1):

    def step(tsk: Tsk):
        lg.info(f'START: {tsk.name}')
        return anext(tsk.gen)

    tsks = deque(tsks)
    wait = defaultdict(list)
    done = set()

    while tsks:
        head = [tsks.popleft() for _ in range(min(parallelism, len(tsks)))]

        results = await asyncio.gather(
            *(step(tsk) for tsk in head),
            return_exceptions=True)

        assert len(head) == len(results)

        for tsk, res in zip(head, results):
            if isinstance(res, Need) and res.val not in done:
                wait[res.val].append(tsk)

            elif isinstance(res, Make):
                done.add(res.val)
                for w in wait.pop(res.val, []):
                    tsks.append(w)
                tsks.append(tsk)

            elif isinstance(res, Tsk):
                tsks.append(res)
                tsks.append(tsk)

            elif isinstance(res, StopAsyncIteration):
                lg.info(f'END: {tsk.name}')

            else:
                lg.error(f'Failed to run {tsk.name}: {res}')

    if wait:
        print(f'Could not run all tasks: {wait}')

    else:
        print('All tasks finished.')

    return wait
