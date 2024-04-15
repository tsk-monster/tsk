# tsk.monster
## A cute little task runner.

![](https://tsk.monster/tsk.svg)

```python
from tsk_monster import run_jobs, tsk

run_jobs(
    tsk(
        'wget -O large.jpg https://picsum.photos/200/300',
        prods=['large.jpg']),

    tsk(
        'convert -resize 100x large.jpg small.jpg',
        needs=['large.jpg'],
        prods=['small.jpg']))
```
Using a `tskfile.py`:
```python
from tsk_monster import tsk

def download_image():
    yield tsk(
        'wget -O large.jpg https://picsum.photos/200/300',
        prods=['large.jpg'])

    yield tsk(
        'convert -resize 100x large.jpg small.jpg',
        needs=['large.jpg'],
        prods=['small.jpg'])
```

Then you can run `tsk download_image`
