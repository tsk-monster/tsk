# tsk.monster
## A cute little tsk runner.
<div style="display:flex; justify-content:center;"><img style="max-height:300px" src='tsk.svg' /></div>

### Quick Start

Install:

```
poetry add tsk-monster
```

Write a `tskfile.py`:

```py title="tskfile.py"
{%
    include-markdown "example_1.py"
    comments=false
%}
```

Run:
```
tsk download_image
```

### More Examples

#### Download multiple images in parallel:

```py title="tskfile.py"
{%
    include-markdown "example_2.py"
    comments=false
%}
```

```
tsk download_images
```

#### Publish your project

```py title="tskfile.py"
{%
    include-markdown "example_3.py"
    comments=false
%}
```

```
tsk publish
```

#### Dynamic Dependencies

```py title="tskfile.py"
{%
    include-markdown "example_4.py"
    comments=false
%}
```

```
tsk thumbnails
```
