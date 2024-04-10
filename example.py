import logging
from pathlib import Path

from tsk_monster import run, shell

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        datefmt='%H:%M:%S',
        format='%(asctime)s [%(levelname)s] %(message)s')

    run(
        shell(
            'wget -o img1.jpg https://picsum.photos/200',
            outputs=[Path('img1.jpg')]))
