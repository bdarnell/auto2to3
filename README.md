Overview
========

`auto2to3` makes it easier and faster to use `2to3` to develop for
Python 2 and 3 simultaneously.  You can continue to work on the
original 2.x code, and `auto2to3` converts modules to Python 3
automatically at import time. `2to3` can be rather slow, so `auto2to3`
caches its output between runs so it only needs to run `2to3` when the
source files change.

Usage
=====

Install `auto2to3` as usual using `pip`/`easy_install`.  Note that `auto2to3`
must be installed under Python 3 (it has only been tested with Python 3.2).

The `auto2to3` script supports a subset of the python interpreter's interface:

    auto2to3 -m mypackage.main_module
    auto2to3 mypackage/script.py

By default, all modules imported from a subdirectory of the current
directory will be run through `2to3`.  To change this behavior, use the
`--package` or `--dir` flags to `auto2to3` to specify which packages or
directories contain Python 2 code that should be converted.

Finishing Touches
=================

`auto2to3` is a development tool; when you're ready to release a
package that was developed with `auto2to3` you should use
`setuptool`'s ability to run `2to3` as a part of the build process.
In your `setup.py` file, simply `import setuptools` and pass
`use_2to3=True` as a keyword argument to the `setup()` function.
Don't forget to remove or exclude `auto2to3`'s cache files from the
distribution (add `global-exclude _auto2to3*` to `MANIFEST.in`, and
add a similar pattern to your `.gitignore` or equivalent)

Acknowledgements
================

Based on `auto2to3.py` by Georg Brandl:
<http://dev.pocoo.org/hg/sandbox/file/tip/auto2to3.py>
