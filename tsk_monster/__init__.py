import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import (Any, AsyncGenerator, Awaitable, Callable, Iterable, List,
                    Union)

lg = logging.getLogger(__name__)


@dataclass
class need:
    val: Any


@dataclass
class make:
    val: Any


def changed(path: Path):
    try:
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
    gen: AsyncGenerator[Union[need, make, "Tsk"], None]

    def __repr__(self):
        return self.name


def tsk(
        description: str, *,
        action: str | Callable[[], Awaitable],
        needs: List[Path] = [],
        makes: List[Path] = []):

    def str2action(s: str):
        async def action():
            p = await asyncio.create_subprocess_shell(s)
            print(p)
            await p.communicate()

        return action

    if isinstance(action, str):
        action = str2action(action)

    async def gen():
        always_run = len(needs) == len(makes) == 0

        for n in needs:
            yield need(n)

        if any(map(changed, needs)) or not all(map(Path.exists, makes)) or always_run:
            lg.info(f'STARTING: {description}')
            await action()
            lg.info(f'DONE: {description}')

        else:
            lg.info(f'SKIPPING: {description}')

        for m in makes:
            lg.debug(f'Creating {m} {m.exists()}')

            if m.exists():
                yield make(m)
            else:
                lg.warning(f'Failed to create {m}.')

    return Tsk(description, gen())


async def runner(tsks: Iterable[Tsk], parallelism=100):

    tsks = deque(tsks)
    wait = defaultdict(list)
    done = set()

    while tsks:
        batch = [
            tsks.popleft()
            for _ in range(min(parallelism, len(tsks)))]

        results = await asyncio.gather(
            *(anext(tsk.gen) for tsk in batch),
            return_exceptions=True)

        assert len(batch) == len(results)

        for tsk, res in zip(batch, results):
            lg.debug(f'{tsk} -> {res}')

            if isinstance(res, need):
                if res.val in done:
                    tsks.append(tsk)
                else:
                    wait[res.val].append(tsk)
                continue

            if isinstance(res, make):
                done.add(res.val)
                for w in wait.pop(res.val, []):
                    tsks.append(w)

                tsks.append(tsk)
                continue

            if isinstance(res, Tsk):
                tsks.append(res)
                tsks.append(tsk)
                continue

            if isinstance(res, StopAsyncIteration):
                pass

            if not isinstance(res, (need, make, Tsk, StopAsyncIteration)):
                lg.error(f'Failed to run {tsk.name}: {res}')

    if wait:
        lg.warning(f'Could not run all tasks: {wait.values()}')
        return

    lg.info('All tasks finished.')


def run(*tsks: Tsk, parallelism=1):
    asyncio.run(runner(tsks, parallelism=parallelism))
