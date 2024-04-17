import pytest

from tsk_monster import job


def test_sort_jobs():
    from tsk_monster import sort
    j1 = job(needs={1})
    j2 = job(prods={1})
    jobs = sort([j1, j2])

    assert jobs == [j2, j1], jobs


def test_validate_jobs():
    from tsk_monster import validate
    j1 = job(needs={1})
    j2 = job(prods={1})
    jobs = validate([j1, j2])

    assert jobs == [j1, j2], jobs

    with pytest.raises(ValueError):
        validate([job(needs={1}, prods={1})])

    with pytest.raises(ValueError):
        validate([job(needs={1}, prods={2})])

    with pytest.raises(ValueError):
        validate([job(needs={1}, prods={2}), job(needs={2}, prods={1})])

    with pytest.raises(ValueError):
        validate([job(needs={1}, prods={2}), job(needs={2}, prods={3})])
