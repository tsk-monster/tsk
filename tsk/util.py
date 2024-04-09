from pathlib import Path
from typing import Iterable


def need(val):
    return (True, val)


def push(val):
    return (False, val)


def change(path: str | Path):
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
