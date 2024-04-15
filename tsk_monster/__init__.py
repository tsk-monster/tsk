'''A cute little task runner.

Examples:
    >>> from tsk_monster import run, tsk
    >>> run(
    ...     tsk(
    ...         'wget -O img.jpg https://picsum.photos/200/300',
    ...         prods=['img.jpg']),
    ...
    ...     tsk(
    ...         'convert -resize 100x img.jpg img.small.jpg',
    ...         needs=['img.jpg'],
    ...         prods=['img.small.jpg']))
'''

import logging
import os
import queue
import threading
from concurrent.futures import Future, ProcessPoolExecutor
from dataclasses import dataclass
from functools import cmp_to_key, partial
from inspect import getmembers, isgeneratorfunction
from pathlib import Path
from typing import Any, Callable, Generator, Iterable, List, Set

import typer
from typing_extensions import Annotated

lg = logging.getLogger(__name__)


@dataclass
class Cmd:
    description: str
    action: Callable[[], Any]

    @classmethod
    def from_str(cls, cmd: str):
        return cls(cmd, partial(os.system, cmd))

    def __repr__(self) -> str:
        return self.description


@dataclass
class Job:
    needs: Set[Any]
    prods: Set[Any]
    cmds: Generator[Cmd, None, None]


def job(*, needs=set(), prods=set(), cmds=[]):
    return Job(needs, prods, cmds)


def sort_jobs(jobs: Iterable[Job]):
    def cmp(a: Job, b: Job):
        if a.needs & b.prods and b.needs & a.prods:
            raise ValueError(f'Jobs {a} and {b} are in a cycle')

        if a.prods & b.needs:
            return -1

        if b.prods & a.needs:
            return 1

        return 0

    return sorted(jobs, key=cmp_to_key(cmp))


def validate(jobs: Iterable[Job]):
    needs = set()
    prods = set()

    for job in sort_jobs(jobs):
        if job.needs & job.prods:
            raise ValueError(f'Job {job} has conflicting needs and prods')

        needs.update(job.needs)
        prods.update(job.prods)

    if not needs.issubset(prods):
        raise ValueError(f'Dependencies not met: {needs - prods}')

    return jobs


def run_jobs(*jobs: Job):
    '''Run jobs in parallel, respecting dependencies.

    Args:
        *jobs: A list of jobs to run.


    Examples:
        >>> from tsk_monster import run, tsk
        >>> run(
        ...     tsk(
        ...         'wget -O img.jpg https://picsum.photos/200/300',
        ...         prods=['img.jpg']),
        ...
        ...     tsk(
        ...         'convert -resize 100x img.jpg img.small.jpg',
        ...         needs=['img.jpg'],
        ...         prods=['img.small.jpg']))
    '''

    q = queue.Queue[Job]()
    pending = []

    def worker():
        prods = set()

        with ProcessPoolExecutor() as executor:
            def run_job(job: Job):
                def done(future: Future):
                    future.result()
                    run_job(job)

                try:
                    cmd = next(job.cmds)
                    lg.info(f'Running {cmd.description}')
                    future = executor.submit(cmd.action)
                    future.add_done_callback(done)

                except StopIteration:
                    prods.update(job.prods)

                    while pending:
                        q.put(pending.pop())
                        q.task_done()

                    q.task_done()

            while True:
                job = q.get()

                if not job.needs.issubset(prods):
                    pending.append(job)
                    continue

                run_job(job)

    threading.Thread(
        target=worker,
        daemon=True).start()

    for job in validate(jobs):
        q.put(job)

    q.join()

    lg.info('All work completed')


Paths = List[Path | str] | List[Path]
Uptodate = Callable[[List[Path], List[Path]], bool]


def uptodate(needs: List[Path], prods: List[Path]):
    def changed(path: Path):
        try:
            tsk = path.with_suffix('.tsk')
            if not tsk.exists():
                return True

            return tsk.stat().st_mtime < path.stat().st_mtime
        finally:
            tsk.touch()

    if len(needs) == 0 and len(prods) == 0:
        return False

    return any(map(changed, needs)) or not all(map(Path.exists, prods))


def lazy_action(
        *, cmd: Cmd,
        needs: List[Path],
        prods: List[Path],
        uptodate: Uptodate):

    if uptodate(needs, prods):
        return

    cmd.action()


def tsk(
        *cmds: Cmd | str,
        needs: Paths = [],
        prods: Paths = [],
        uptodate: Uptodate = uptodate) -> Job:
    '''Create a file based task.

    Examples:
        >>> tsk(
        ...     'wget -O img.jpg https://picsum.photos/200/300',
        ...     prods=['img.jpg'])

    Args:
        cmds: A list of commands to run.
        needs: A list of files that are needed.
        prods: A list of files that will be produced.

    Returns:
        A job.
    '''

    def to_paths(paths: Paths) -> List[Path]:
        return [Path(p) if isinstance(p, str) else p for p in paths]

    cmd_list = [
        Cmd.from_str(cmd) if isinstance(cmd, str) else cmd
        for cmd in cmds]

    return Job(
        set(to_paths(needs)),
        set(to_paths(prods)),
        (Cmd(
            cmd.description,
            partial(
                lazy_action,
                cmd=cmd,
                needs=to_paths(needs),
                prods=to_paths(prods),
                uptodate=uptodate)) for cmd in cmd_list))


def load_tasks():
    module = __import__('tskfile')
    return getmembers(module, isgeneratorfunction)


def task_names(prefix: str):
    return [name for name, _ in load_tasks() if name.startswith(prefix)]


app = typer.Typer()


@ app.command()
def tsk_monster(target: Annotated[str, typer.Argument(autocompletion=task_names)]):
    logging.basicConfig(
        level=logging.INFO,
        datefmt='%H:%M:%S',
        format='%(asctime)s - %(levelname)s - %(message)s')

    module = __import__('tskfile')
    members = getmembers(module, isgeneratorfunction)
    for name, value in members:
        if target == name:
            run_jobs(*value())


def main():
    app()
