# tsk.monster
## A cute little task runner.

### Usage
```python
from pathlib import Path

from tsk_monster import run, tsk

if __name__ == '__main__':
    img1 = Path('img1.jpg')
    img2 = Path('img2.jpg')

    run(
        tsk(
            'Download image',
            action='wget -o img1.jpg https://picsum.photos/200',
            outputs=[img1]),

        tsk(
            'Resize image',
            action='convert img1.jpg -resize 100 img2.jpg',
            inputs=[img1],
            outputs=[img2]))
```

### Features
- Zero dependencies
- Concise API
- Async and parallel execution
- Tasks run only when needed


### Non-file dependencies
You can use any type of dependencies and write your own logic like so:
```python
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

```
