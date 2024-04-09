from dataclasses import dataclass
from typing import Any, Generator, Set

tsk = Generator[Any, None, None]


@dataclass
class pull:
    pass


@dataclass
class push:
    pass


def run(tsks: Set[tsk]):
    print("Hello World!")


if __name__ == '__main__':
    run(set())
