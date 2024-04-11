import asyncio
import logging

from tsk_monster import Tsk, make, need, run

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    async def ingredients():
        print('Getting Water')
        yield make('Water')
        print('Getting Salt')
        yield make('Salt')
        print('Getting Oil')
        yield make('Oil')
        print('Getting Flour')
        yield make('Flour')
        print('Getting Cheese')
        yield make('Cheese')
        print('Getting Tomato')
        yield make('Tomato')

    async def dough():
        yield need('Water')
        yield need('Salt')
        yield need('Oil')
        yield need('Flour')

        print('Making dough...')

        await asyncio.sleep(3)

        yield make('Dough')

    async def pizza():
        yield need('Dough')
        yield need('Cheese')
        yield need('Tomato')

        print('Making pizza...')

        await asyncio.sleep(2)

        print('Pizza is ready!')

        yield make('Pizza')

    run(
        Tsk('Get ingredients', ingredients()),
        Tsk('Make dough', dough()),
        Tsk('Make pizza', pizza()))
