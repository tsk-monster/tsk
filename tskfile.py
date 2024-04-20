
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
