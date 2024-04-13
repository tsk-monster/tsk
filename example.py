import logging

from tsk_monster import Job, need, prod, run

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def action():
        print('lala')

    def actions1():
        yield action
        yield prod(1)

    def actions2():
        yield need(1)
        yield action

    print()
    run(
        Job('Job1', actions1()),
        Job('Job2', actions2())
    )
