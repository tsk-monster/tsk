from tsk_monster import tsk


def publish():
    yield tsk(
        'poetry version patch',
        'git add -A',
        'git commit -am "$(poetry version)"',
        prods=['pyproject.toml'])

    yield tsk(
        'mkdocs gh-deploy; poetry publish --build',
        needs=['pyproject.toml'])
