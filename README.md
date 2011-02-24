Overview
========

`auto2to3` is a wrapper to run `2to3` automatically at import time.  This is
useful when developing a library that intends to support both Python 2 and
Python 3 via `2to3`.  

Usage
=====

`auto2to3.py --package=pkg main_module`

main_module is run as if by the -m flag to the python interpreter
(i.e. __name__ == '__main__').  All modules whose name begins with a name
passed to the --package flag (which may be specified more than once)
will be run through 2to3.  2to3 output is cached on disk between runs
for speed.

Example
-------

`auto2to3.py --package=tornado tornado.test.runtests`

Acknowledgements
================

Based on auto2to3.py by Georg Brandl:
http://dev.pocoo.org/hg/sandbox/file/tip/auto2to3.py
