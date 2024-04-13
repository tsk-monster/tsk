import logging

from tsk_monster import run, tsk

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt='%H:%M:%S',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    run(
        tsk(
            'wget -O img1.jpg https://picsum.photos/200/300',
            prods=['img1.jpg']),

        tsk(
            'convert -resize 100x img1.jpg img1.small.jpg',
            needs=['img1.jpg'],
            prods=['img1.small.jpg']))
