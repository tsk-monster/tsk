from tsk_monster import tsk


def download_image():
    yield tsk(
        'wget -O large.jpg https://picsum.photos/200/300',
        prods=['large.jpg'])

    yield tsk(
        'convert -resize 100x large.jpg small.jpg',
        needs=['large.jpg'],
        prods=['small.jpg'])
