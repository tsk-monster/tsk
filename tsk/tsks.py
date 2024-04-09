import os
from pathlib import Path
from typing import List

from tsk import run
from tsk.util import change, need, push


def shell(cmd: str, *, deps: List[Path] = [], targets: List[Path] = []):
    for d in deps:
        yield need(d)

    if any(map(change, deps)) or not all(map(Path.exists, targets)):
        print('Executing:', cmd)
        os.system(cmd)

    assert all(map(Path.exists, targets)), 'Failed to create targets.'

    for t in targets:
        yield push(t)


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
