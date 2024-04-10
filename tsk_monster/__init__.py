import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import (Any, AsyncGenerator, Awaitable, Callable, Iterable, List,
                    Union)

lg = logging.getLogger(__name__)


@dataclass
class input:
    val: Any


@dataclass
class output:
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
    gen: AsyncGenerator[Union[input, output, "Tsk"], None]

    def __repr__(self):
        return self.name


def tsk(
        name: str, action: Callable[[], Awaitable], *,
        inputs: List[Path] = [],
        outputs: List[Path] = []):

    async def gen():
        always_run = len(inputs) == len(outputs) == 0

        for n in inputs:
            yield input(n)

        if any(map(changed, inputs)) or not all(map(Path.exists, outputs)) or always_run:
            lg.info(f'STARTING: {name}')
            await action()
            lg.info(f'DONE: {name}')

        else:
            lg.info(f'SKIPPING: {name}')

        for m in outputs:
            if m.exists():
                yield output(m)
            else:
                lg.warning(f'Failed to create {m}.')

    return Tsk(name, gen())


def shell(
        cmd: str, *,
        need: List[Path] = [],
        make: List[Path] = []):

    return tsk(
        cmd, lambda: asyncio.create_subprocess_shell(cmd),
        inputs=need,
        outputs=make)


async def runner(tsks: Iterable[Tsk], parallelism=1):

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
            if isinstance(res, input) and res.val not in done:
                wait[res.val].append(tsk)

            elif isinstance(res, output):
                done.add(res.val)
                for w in wait.pop(res.val, []):
                    tsks.append(w)
                tsks.append(tsk)

            elif isinstance(res, Tsk):
                tsks.append(res)
                tsks.append(tsk)

            elif isinstance(res, StopAsyncIteration):
                pass

            else:
                lg.error(f'Failed to run {tsk.name}: {res}')

    if wait:
        lg.warning(f'Could not run all tasks: {wait.values()}')
        return

    lg.info('All tasks finished.')


def run(*tsks: Tsk, parallelism=1):
    asyncio.run(runner(tsks, parallelism=parallelism))
