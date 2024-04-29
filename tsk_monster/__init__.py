'''
tsk.monster - A cute little tsk runner
'''
import logging
import os
import queue
import threading
from concurrent.futures import Future, ProcessPoolExecutor
from dataclasses import dataclass
from functools import cmp_to_key, partial
from hashlib import shake_128
from inspect import getmembers, isgeneratorfunction
from pathlib import Path
from typing import (Any, Callable, Generator, Generic, Iterable, List, Set,
                    TypeVar)

import typer
from dill import dumps, loads
from typing_extensions import Annotated

T = TypeVar('T')
Paths = List[Path | str] | List[Path]
Action = Callable[[], Any]
Predicate = Callable[[], bool]

lg = logging.getLogger(__name__)


class Function(Generic[T]):
    def __init__(self, action: Action) -> None:
        self.action = dumps(action)

    def __call__(self) -> T:
        action = loads(self.action)
        return action()


class Cmd:
    '''
    A cmd is an action that is conditionally run based on a predicate.

    Args:
        action: The action that needs to be run.
        need_to_run: A predicate that determines if the action needs to be run.
    '''
    action: Function[Any]
    need_to_run: Function[bool]

    def __init__(
            self, *,
            action: Action,
            need_to_run: Predicate,
            desc=''):

        self.desc = desc
        self.action = Function(action)
        self.need_to_run = Function(need_to_run)

    @classmethod
    def from_str(cls, cmd: str, need_to_run: Predicate):
        return cls(
            desc=cmd,
            action=partial(os.system, cmd),
            need_to_run=need_to_run)

    def __call__(self):
        try:
            if self.need_to_run():
                lg.info(f'[RUNNING] {self}')
                return self.action()
            else:
                lg.info(f'[SKIPPING] {self}')
        except Exception as e:
            lg.error(e)

    def __repr__(self):
        return self.desc

    def __str__(self):
        return self.desc


@dataclass
class Job:
    '''
    A job is a set of commands that need to be run in order to produce a set of artifacts.
    Artifacts can be files, directories, or any other kind of object.
    A job can also depend on other artifacts that are produced by other jobs.

    Args:
        needs: A set of artifacts that are required by this job.
        prods: A set of artifacts that are produced by this job.
        cmds: A generator of commands that need to be run in order to produce the artifacts.
    '''
    needs: Set[Any]
    prods: Set[Any]
    cmds: Generator[Cmd, None, None]


def job(*,
        cmds: Generator[Cmd, None, None] = (_ for _ in []),
        needs=set(),
        prods=set()):

    return Job(needs, prods, cmds)


def sort(jobs: Iterable[Job]):
    def cmp(a: Job, b: Job):
        if (a.needs & b.prods) and (b.needs & a.prods):
            raise ValueError(f'Jobs {a} and {b} are in a cycle')

        if a.prods & b.needs:
            return -1

        if b.prods & a.needs:
            return 1

        return 0

    return sorted(jobs, key=cmp_to_key(cmp))


def validate(jobs: Iterable[Job]):

    for job in jobs:
        if not isinstance(job, Job):
            raise ValueError(f'Expected a Job, got {job}')

    needs = set()
    prods = set()

    for job in sort(jobs):
        if job.needs & job.prods:
            raise ValueError(f'Job {job} has conflicting needs and prods')

        needs |= job.needs
        prods |= job.prods

    if not needs.issubset(prods):
        raise ValueError(f'Dependencies not met: {needs - prods}')

    return jobs


def monster(*jobs: Job):
    '''
    Executes a set of jobs in parallel.

    Args:
        jobs: A set of jobs that need to be run.
    '''
    lg.debug(f'Running jobs: {jobs}')
    q = queue.Queue[Job]()
    pending = []

    def worker():
        prods = set()

        with ProcessPoolExecutor() as executor:
            def run_job(job: Job):
                def done(future: Future):
                    try:
                        future.result()
                        run_job(job)
                    except Exception as e:
                        lg.error(e)
                        exit(1)

                try:
                    cmd = next(job.cmds)
                    lg.info(f'[PROCESSING] {cmd}')
                    future = executor.submit(cmd)
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
        lg.debug(f'[ENQUEUE] {job}')
        q.put(job)

    q.join()

    lg.info('GOOD JOB!')


def exist(*paths: Path | str):
    '''
    Signal that a set of paths already exist.

    Args:
        paths: A set of paths that already exist.

    Returns:
        A dummy job that does nothing.
    '''
    return Job(
        needs=set(),
        prods={Path(p) for p in paths},
        cmds=(_ for _ in []))


def to_paths(paths: Paths) -> List[Path]:
    return [Path(p) if isinstance(p, str) else p for p in paths]


def run(
        *actions: Action | str,
        needs: Paths = [],
        prods: Paths = []):
    '''
    Create a job that always runs a set of actions.

    Args:
        actions: A set of actions that need to be run.
        needs: A set of artifacts that are required by this job.
        prods: A set of artifacts that are produced by this job.
    '''
    return Job(
        needs=set(to_paths(needs)),
        prods=set(to_paths(prods)),
        cmds=(
            Cmd.from_str(action, lambda: True) if isinstance(action, str)
            else Cmd(action=action, need_to_run=lambda: True)
            for action in actions))


def tsk(
        *actions: Action | str,
        desc: str = '',
        needs: Paths = [],
        prods: Paths = [],
        updts: Paths = []) -> Job:
    '''
    Create a job. The job will only run if any of the following conditions are met:
    - Any of the artifacts in `needs` has been updated since the last run.
    - Any of the artifacts in `prods` does not exist.
    - The `updts` list is not empty.

    Args:
        actions: A set of actions that need to be run.
        desc: A description of the job.
        needs: A set of artifacts that are required by this job.
        prods: A set of artifacts that are produced by this job.
        updts: A set of artifacts that are updated by this job.
    '''
    def need_to_run(action: str | Action):
        def changed(path: Path):
            try:
                hash = shake_128(dumps(action)).hexdigest(8)
                tsk = path.with_suffix(f'.{hash}.tsk')
                if not tsk.exists():
                    return True

                return tsk.stat().st_mtime < path.stat().st_mtime
            finally:
                tsk.touch()

        return \
            len(updts) > 0 \
            or any(map(changed, to_paths(needs))) \
            or not all(map(Path.exists, to_paths(prods)))

    cmds = (
        Cmd.from_str(
            action,
            partial(need_to_run, action)) if isinstance(action, str)

        else Cmd(
            desc=desc,
            action=action,
            need_to_run=partial(need_to_run, action))

        for action in actions)

    return Job(
        set(to_paths(needs)),
        set(to_paths(prods)) | set(to_paths(updts)),
        cmds)


app = typer.Typer()


def task_names(prefix: str):
    def load_tasks():
        module = __import__('tskfile')
        return getmembers(module, isgeneratorfunction)

    return [name for name, _ in load_tasks() if name.startswith(prefix)]


@app.command()
def tsk_monster(targets: Annotated[List[str], typer.Argument(autocompletion=task_names)]):
    from rich.logging import RichHandler

    logging.basicConfig(
        level=logging.INFO,
        datefmt='%H:%M:%S',
        format='%(asctime)s - %(message)s',
        handlers=[RichHandler()])

    module = __import__('tskfile')
    members = getmembers(module, isgeneratorfunction)
    members = dict(members)

    for target in targets:
        lg.info(f'[TARGET] {target}')
        monster(*members[target]())


def main():
    app()
