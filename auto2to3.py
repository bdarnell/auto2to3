#!/usr/bin/env python3.2
"""Wrapper to run 2to3 automatically at import time.

Usage:
  auto2to3.py main_module

main_module is run as if by the -m flag to the python interpreter
(i.e. __name__ == '__main__').  It must be specified as a module name,
not a filename (e.g. tornado.test.runtests, not tornado/test/runtests.py)

All modules whose name begins wtih a prefix passed to the --package or --dir
flags (which may be specified more than once) will be run through 2to3.
--package is compared to the python module name, while --dir uses the path
in the filesystem.  If neither --package or --dir is specified, the current
directory is assumed, which is often sufficient.

2to3 output is cached on disk between runs for speed.

Based on auto2to3.py by Georg Brandl:
http://dev.pocoo.org/hg/sandbox/file/tip/auto2to3.py
"""

import argparse
import os
import sys
import imp
import runpy
from io import StringIO
from pkgutil import ImpImporter, ImpLoader
import runpy
import sys
import tempfile

import lib2to3
from lib2to3.refactor import RefactoringTool, get_fixers_from_package

fixes = get_fixers_from_package('lib2to3.fixes')
rt = RefactoringTool(fixes)

PACKAGES = []
DIRS = []

def maybe_2to3(filename, modname=None):
    """Returns a python3 version of filename."""
    need_2to3 = False
    filename = os.path.abspath(filename)
    if any(filename.startswith(d) for d in DIRS):
        need_2to3 = True
    elif modname is not None and any(modname.startswith(p) for p in PACKAGES):
        need_2to3 = True
    if not need_2to3:
        return filename
    outfilename = '/_auto2to3_'.join(os.path.split(filename))
    if (not os.path.exists(outfilename) or
        os.stat(filename).st_mtime > os.stat(outfilename).st_mtime):
        try:
            with open(filename) as file:
                contents = file.read()
            contents = rt.refactor_docstring(contents, filename)
            tree = rt.refactor_string(contents, filename)
        except Exception as err:
            raise ImportError("2to3 couldn't convert %r" % filename)
        outfile = open(outfilename, 'wb')
        outfile.write(str(tree).encode('utf8'))
        outfile.close()
    return outfilename



class ToThreeImporter(ImpImporter):
    def find_module(self, fullname, path=None):
        # this duplicates most of ImpImporter.find_module
        subname = fullname.split(".")[-1]
        if subname != fullname and self.path is None:
            return None
        if self.path is None:
            path = None
        else:
            path = [os.path.realpath(self.path)]
        try:
            file, filename, etc = imp.find_module(subname, path)
        except ImportError:
            return None
        if file and etc[2] == imp.PY_SOURCE:
            outfilename = maybe_2to3(filename, modname=fullname)
            if outfilename != filename:
                file.close()
                filename = outfilename
                file = open(filename, 'rb')
        return ImpLoader(fullname, file, filename, etc)


# setup the hook
sys.path_hooks.append(ToThreeImporter)
for key in sys.path_importer_cache:
    if sys.path_importer_cache[key] is None:
        sys.path_importer_cache[key] = ToThreeImporter(key)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', action='append')
    parser.add_argument('--dir', action='append')
    parser.add_argument('-m', action='store', metavar='MODULE')
    args, rest = parser.parse_known_args()
    if args.package:
        PACKAGES.extend(args.package)
    if args.dir:
        DIRS.extend(os.path.abspath(d) for d in args.dir)
    if not PACKAGES and not DIRS:
        DIRS.append(os.getcwd())
    if args.m:
        sys.argv[1:] = rest
        runpy.run_module(args.m, run_name='__main__', alter_sys=True)
    elif rest:
        sys.argv = rest
        converted = maybe_2to3(rest[0])
        with open(converted) as f:
            new_globals = dict(__name__='__main__',
                               __file__=rest[0])
            exec(f.read(), new_globals)
    else:
        import code
        code.interact()

if __name__ == '__main__':
    main()
