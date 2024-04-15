# Quick Start

## Installation
```bash
poetry add tsk-monster
```

Create a `tskfile.py` with the following content:
```python
def download_image():
    yield tsk(
        'wget -O img.jpg https://picsum.photos/200/300',
        prods=['img.jpg'])

    yield tsk(
        'convert -resize 100x img.jpg img.small.jpg',
        needs=['img.jpg'],
        prods=['img.small.jpg'])
```
