#!/usr/bin/env python3.2
#
# Import hook to run 2to3 transparently over imported files.
# Only works with files that have 'python2' in the first or second line.
#

import argparse
import os
import sys
import imp
import runpy
from io import StringIO
from pkgutil import ImpImporter, ImpLoader
import runpy
import tempfile

import lib2to3
from lib2to3.refactor import RefactoringTool

sys.path.append(os.path.dirname(lib2to3.__file__))

class DummyOptions:
    fix = []
    def __getattr__(self, name):
        return None

opt = DummyOptions()

rt = RefactoringTool(opt)

PACKAGES = []

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
            filename = '<%r converted by 2to3>' % filename
            line1 = file.readline()
            line2 = file.readline()
            file.seek(0)
            if 'python2' in line1 or 'python2' in line2:
                try:
                    tree = rt.driver.parse_stream(file)
                except Exception as err:
                    raise ImportError("2to3 couldn't convert %r" % filename)
                finally:
                    file.close()
                if rt.refactor_tree(tree, filename):
                    file = tempfile.TemporaryFile()
                    file.write(str(tree).encode('utf8'))
                    file.seek(0)
        return ImpLoader(fullname, file, filename, etc)


# setup the hook
sys.path_hooks.append(ToThreeImporter)
for key in sys.path_importer_cache:
    if sys.path_importer_cache[key] is None:
        sys.path_importer_cache[key] = ToThreeImporter(key)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', action='append')
    parser.add_argument('main')
    args = parser.parse_args()
    if args.package:
        PACKAGES.extend(args.package)
    runpy.run_module(args.main)

if __name__ == '__main__':
    main()
