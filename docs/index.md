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

### Parallel Execution
tsk.monster executes independent tasks in parallel and utilizes all available CPU cores on the machine.
Here is an example:

```py title="tskfile.py"
{%
    include-markdown "example_2.py"
    comments=false
%}
```

```
tsk download_images
```

### Prevent Unnecessary Work

There are three situations in which a task is executed:

1. If any of the `prods` files are missing.
2. If any of the `needs` files were updated since the last run.
3. If the `updts` list is not empty.

In all other situations, the task is considered up to date and is skipped.

In the following example, the first task will be executed only if the file `lazy.txt` is missing. The second task will always be executed (if yielded), and the third task will be executed only if `lazy.txt` was updated (touched) since the last run.
```py title="tskfile.py"
{%
    include-markdown "example_3.py"
    comments=false
%}
```

```
tsk publish
```

### Dynamic Execution

```py title="tskfile.py"
{%
    include-markdown "example_4.py"
    comments=false
%}
```

```
tsk thumbnails
```
