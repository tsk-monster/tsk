import logging
import os
import queue
import threading
from collections import defaultdict
from concurrent.futures import Future, ProcessPoolExecutor
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any, Callable, Generator, List

lg = logging.getLogger(__name__)


@dataclass
class need:
    val: Any


@dataclass
class prod:
    val: Any


@dataclass
class Job:
    description: str
    gen: Generator[need | prod | Callable, None, None]

    def __repr__(self):
        return self.description


def run(*jobs: Job):
    q = queue.Queue[Job]()
    needs = defaultdict(list)
    prods = set()

    def worker():
        def add2q(job: Job):
            def _(future: Future):
                future.result()
                q.put(job)
                q.task_done()

            return _

        with ProcessPoolExecutor() as executor:
            while True:
                job = q.get()

                try:
                    item = next(job.gen)

                    if isinstance(item, Callable):
                        lg.info(f'Submitting: {job}')
                        future = executor.submit(item)
                        future.add_done_callback(add2q(job))

                    if isinstance(item, need):
                        lg.debug(f'{job} needs {item.val}')

                        if item.val in prods:
                            q.put(job)
                            q.task_done()
                        else:
                            needs[item.val].append(job)

                    if isinstance(item, prod):
                        lg.debug(f'{job} produced {item.val}')

                        prods.add(item.val)
                        q.put(job)
                        q.task_done()

                        jobs = needs.pop(item.val, [])

                        for job in jobs:
                            q.put(job)
                            q.task_done()

                except StopIteration:
                    lg.info(f'Done {job}')
                    q.task_done()

    threading.Thread(
        target=worker,
        daemon=True).start()

    for job in jobs:
        q.put(job)

    q.join()

    lg.info('All work completed')


def changed(path: Path):
    try:
        tsk = path.with_suffix('.tsk')
        if not tsk.exists():
            return True

        return tsk.stat().st_mtime < path.stat().st_mtime
    finally:
        tsk.touch()


@dataclass
class Cmd:
    description: str
    action: Callable[[], Any]

    def __repr__(self) -> str:
        return self.description


Paths = List[Path | str] | List[Path]


def to_paths(paths: Paths) -> List[Path]:
    return [Path(p) if isinstance(p, str) else p for p in paths]


def tsk(
        cmd: str | Cmd, *,
        needs: Paths = [],
        prods: Paths = []):

    if isinstance(cmd, str):
        cmd = Cmd(cmd, partial(os.system, cmd))

    needs = to_paths(needs)
    prods = to_paths(prods)

    def gen():
        for n in needs:
            yield need(n)

        if any(map(changed, needs)) or not all(map(Path.exists, prods)):
            yield cmd.action

        else:
            lg.info(f'SKIPPING: {cmd.description}')

        for m in prods:
            if m.exists():
                yield prod(m)
            else:
                raise Exception(f'{cmd} failed to produce {m}.')

    return Job(cmd.description, gen())
