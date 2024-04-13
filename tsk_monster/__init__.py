import logging
import queue
import threading
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Generator

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
        while True:
            job = q.get()
            lg.debug(f'Processing job {job}')

            try:
                item = next(job.gen)
                lg.debug(f'Next item {item}')

                if isinstance(item, Callable):
                    item()
                    q.put(job)

                if isinstance(item, need):
                    if item.val in prods:
                        q.put(job)
                    else:
                        needs[item.val].append(job)

                if isinstance(item, prod):
                    prods.add(item.val)
                    q.put(job)
                    jobs = needs.pop(item.val, set())

                    for job in jobs:
                        q.put(job)

            except StopIteration:
                print(f'{job} completed')

            finally:
                q.task_done()

    threading.Thread(
        target=worker,
        daemon=True).start()

    for job in jobs:
        q.put(job)

    q.join()

    print('All work completed')
