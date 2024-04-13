import logging
import os
from pathlib import Path
from typing import Callable, Iterable, List

from tsk_monster import Job, need, prod

lg = logging.getLogger(__name__)


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


def tsk(
        description: str, *,
        action: str | Callable[[], None],
        needs: List[Path] = [],
        makes: List[Path] = []):

    def str2action(s: str):
        def action():
            os.system(s)

        return action

    if isinstance(action, str):
        action = str2action(action)

    def gen():
        always_run = len(needs) == len(makes) == 0

        for n in needs:
            yield need(n)

        if any(map(changed, needs)) or not all(map(Path.exists, makes)) or always_run:
            lg.info(f'STARTING: {description}')
            action()
            lg.info(f'DONE: {description}')

        else:
            lg.info(f'SKIPPING: {description}')

        for m in makes:
            if m.exists():
                yield prod(m)
            else:
                lg.warning(f'Failed to create {m}.')

    return Job(description, gen())
