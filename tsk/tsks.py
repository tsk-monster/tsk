import asyncio
import logging
from pathlib import Path
from typing import Awaitable, Callable, List

import tsk.util as utl
from tsk import Tsk, plan

lg = logging.getLogger(__name__)


def tsk(
        name: str, action: Callable[[], Awaitable], *,
        need: List[Path] = [],
        make: List[Path] = []):

    async def gen():
        always_run = len(need) == len(make) == 0

        for n in need:
            yield utl.need(n)

        if any(map(utl.changed, need)) or not all(map(Path.exists, make)) or always_run:
            await action()

        for m in make:
            if m.exists():
                yield utl.make(m)
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    asyncio.run(
        plan([
            shell('wget https://picsum.photos/200'),
            shell('wget https://picsum.photos/200'),
            shell('wget https://picsum.photos/200'),
            shell('wget https://picsum.photos/200'),
            shell('wget https://picsum.photos/200'),
        ]))
