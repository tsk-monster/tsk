# tsk.monster
## A cute little task runner.

![](https://tsk.monster/tsk.small.jpg)

```python
from tsk_monster import run, tsk

run(
    tsk(
        'wget -O img1.jpg https://picsum.photos/200/300',
        prods=['img1.jpg']),

    tsk(
        'convert -resize 100x img1.jpg img1.small.jpg',
        needs=['img1.jpg'],
        prods=['img1.small.jpg']))
```
