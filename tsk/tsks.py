import os
from pathlib import Path
from typing import Any, Callable, Generator, List, Tuple

import tsk.util as utl
from tsk import run

Tsk = Generator[Tuple[bool, Any], None, None]


def tsk(
        action: Callable, *,
        need: List[Path] = [],
        make: List[Path] = []):

    for d in need:
        yield utl.need(d)

    if any(map(utl.change, need)) or not all(map(Path.exists, make)):
        action()

    assert all(map(Path.exists, make)), 'Failed to create targets.'

    for t in make:
        yield utl.make(t)


def shell(
        cmd: str, *,
        deps: List[Path] = [],
        targets: List[Path] = []):

    return tsk(lambda: os.system(cmd), need=deps, make=targets)


if __name__ == '__main__':
    tmp1_txt = Path('tmp1.txt')
    tmp2_txt = Path('tmp2.txt')

    run([
        shell(
            'touch tmp1.txt',
            targets=[tmp1_txt]),

        shell(
            'touch tmp2.txt',
            deps=[tmp2_txt],
            targets=[tmp1_txt])])
