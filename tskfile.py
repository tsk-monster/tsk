from tsk_monster import tsk


def publish():
    yield tsk(
        'poetry version patch',
        'git add -A',
        'git commit -am "$(poetry version)"',
        'poetry publish --build',

        prods=['pyproject.toml'])

    yield tsk(
        'mkdocs gh-deploy',

        needs=['pyproject.toml'])
