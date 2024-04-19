from tsk_monster import tsk


def download_image(i=0):
    large = f'large_{i:02}.jpg'
    small = f'small_{i:02}.jpg'

    yield tsk(
        f'wget -O {large} https://picsum.photos/200/300',
        prods=[large])

    yield tsk(
        f'convert -resize 100x {large} {small}',
        needs=[large],
        prods=[small])


def download_images():
    for i in range(10):
        yield from download_image(i)
