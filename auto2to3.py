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
            if (any(fullname.startswith(p) for p in PACKAGES) or
                any(filename.startswith(d) for d in DIRS)):
                outfilename = '/_auto2to3_'.join(os.path.split(filename))
                if (not os.path.exists(outfilename) or
                    os.stat(filename).st_mtime > os.stat(outfilename).st_mtime):
                    try:
                        contents = file.read()
                        contents = rt.refactor_docstring(contents, filename)
                        tree = rt.refactor_string(contents, filename)
                    except Exception as err:
                        raise ImportError("2to3 couldn't convert %r" % filename)
                    outfile = open(outfilename, 'wb')
                    outfile.write(str(tree).encode('utf8'))
                    outfile.close()
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
    # accept and ignore -m for compatibility with the python interpreter
    parser.add_argument('-m', action='store_true')
    parser.add_argument('main')
    args, rest = parser.parse_known_args()
    if args.package:
        PACKAGES.extend(args.package)
    if args.dir:
        DIRS.extend(args.dir)
    if not PACKAGES and not DIRS:
        DIRS.append(os.getcwd())
    sys.argv[1:] = rest
    runpy.run_module(args.main, run_name='__main__', alter_sys=True)

if __name__ == '__main__':
    main()
