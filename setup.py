from distutils.core import setup

setup(name="auto2to3",
      version="0.3",
      author="Ben Darnell",
      url="https://github.com/bdarnell/auto2to3/",
      py_modules=["auto2to3"],
      scripts=["bin/auto2to3"],
      license="http://www.apache.org/licenses/LICENSE-2.0",
      description="Wrapper to run 2to3 automatically at import time",
      )
