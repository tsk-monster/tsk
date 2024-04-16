from tsk_monster import job


def test_sort_jobs():
    from tsk_monster import sort
    j1 = job(needs={1})
    j2 = job(prods={1})
    jobs = sort([j1, j2])

    assert jobs == [j2, j1], jobs
