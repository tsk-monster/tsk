from random import random

from tsk_monster import tsk


def lazy():
    yield tsk(
        'touch lazy.txt',
        prods=['lazy.txt'])

    if random() < 0.5:
        yield tsk(
            'touch lazy.txt',
            updts=['lazy.txt'])

    yield tsk(
        'echo lazy.txt was updated',
        needs=['lazy.txt'])
