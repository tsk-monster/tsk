from tsk_monster import run, tsk


def publish():
    yield run(
        'poetry version patch',
        'git add -A',
        'git commit -am "$(poetry version)"',
        'poetry publish --build',

        prods=['pyproject.toml'])

    yield tsk(
        'mkdocs gh-deploy',

        needs=['pyproject.toml'])


def download_image():
    yield tsk(
        'wget -O img.jpg https://picsum.photos/200/300',
        prods=['img.jpg'])

    yield tsk(
        'convert -resize 100x img.jpg img.small.jpg',
        needs=['img.jpg'],
        prods=['img.small.jpg'])
