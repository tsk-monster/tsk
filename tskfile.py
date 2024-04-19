from pathlib import Path

from tsk_monster import dummy, tsk


def publish():
    yield tsk(
        'poetry version patch',
        updts=['pyproject.toml'])

    yield tsk(
        'mkdocs gh-deploy',
        needs=['pyproject.toml'])

    yield tsk(
        'poetry publish --build',
        needs=['pyproject.toml'])

    yield tsk(
        'git commit -am "$(poetry version)"',
        needs=['pyproject.toml'])


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


def oops():
    def exception():
        raise Exception('oops')

    yield tsk(
        exception, updts=['none.txt'])


def thumbnails():
    from functools import partial

    from PIL import Image

    def thumbnail(in_path: Path, out_path: Path):
        img = Image.open(in_path)
        img.thumbnail((100, 100))
        img.save(out_path)

    for in_path in Path('imgs').glob('*.jpg'):
        out_path = Path('thumbs') / in_path.name

        yield dummy([in_path])

        yield tsk(
            partial(thumbnail, in_path, out_path),
            needs=[in_path],
            prods=[out_path])
