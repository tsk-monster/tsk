from tsk_monster import tsk


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
