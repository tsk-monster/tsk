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
        need: List[Path] = [],
        make: List[Path] = []):

    return tsk(lambda: os.system(cmd), need=need, make=make)


def echo(txt: str):
    yield print(txt)


if __name__ == '__main__':
    tmp1_txt = Path('tmp1.txt')
    tmp2_txt = Path('tmp2.txt')

    def echo_lines(file: Path):
        yield utl.need(file)

        with open(file) as f:
            for line in f:
                yield echo(line)

    run([
        echo_lines(tmp1_txt),

        shell(
            'echo baba >  tmp1.txt',
            make=[tmp1_txt]),

        shell(
            'touch tmp2.txt',
            need=[tmp1_txt],
            make=[tmp2_txt])])
