import asyncio
import logging

from tsk_monster import plan, shell

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    print()
    print('-----')
    asyncio.run(
        plan([
            shell('wget https://picsum.photos/200'),
            shell('wget https://picsum.photos/200'),
            shell('wget https://picsum.photos/200'),
            shell('wget https://picsum.photos/200'),
            shell('wget https://picsum.photos/200')], parallelism=10))
