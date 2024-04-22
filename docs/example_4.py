from functools import partial
from pathlib import Path

from PIL import Image

from tsk_monster import exist, tsk


def thumbnails():
    def thumbnail(in_path: Path, out_path: Path):
        img = Image.open(in_path)
        img.thumbnail((100, 100))
        img.save(out_path)

    for in_path in Path('imgs').glob('*.jpg'):
        out_path = Path('thumbs') / in_path.name

        # Tells tsk.monster that this file exists
        yield exist(in_path)

        yield tsk(
            partial(thumbnail, in_path, out_path),
            needs=[in_path],
            prods=[out_path])
