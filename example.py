import logging
from pathlib import Path

from tsk_monster import run, tsk

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s')

    img1 = Path('img1.jpg')
    img2 = Path('img2.jpg')

    run(
        tsk(
            'Download image',
            action='wget -O img1.jpg https://picsum.photos/200',
            makes=[img1]),

        tsk(
            'Resize image',
            action='convert img1.jpg -resize 100 img2.jpg',
            needs=[img1],
            makes=[img2]))
