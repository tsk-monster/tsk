
from tsk_monster import run, tsk


def docs():
    yield run(
        'mkdocs gh-deploy')


def publish():
    yield tsk(
        'poetry version patch',
        updts=['pyproject.toml'])

    yield tsk(
        'poetry publish --build',
        needs=['pyproject.toml'])

    yield tsk(
        'git commit -am "$(poetry version)"',
        needs=['pyproject.toml'])


def download_images():
    for i in range(5):
        large = f'large_{i:02}.jpg'
        small = f'small_{i:02}.jpg'

        yield tsk(
            f'wget -nv -O {large} https://picsum.photos/200/300',
            prods=[large])

        yield tsk(
            f'convert -resize 100x {large} {small}',
            needs=[large],
            prods=[small])
