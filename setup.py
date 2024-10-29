#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

from glob import glob
from os.path import abspath, basename, dirname, join, splitext

from setuptools import find_packages, setup

current_directory = abspath(dirname(__file__))
with open(join(current_directory, "README.md"), encoding="utf-8") as readme_file:
    LONG_DESCRIPTION = readme_file.read()

NAME = "shoe_backtest"
VERSION = "1.0.0"
LICENSE = "MIT"
DESCRIPTION = ""
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"
AUTHOR = "Adam Schueller"
AUTHOR_EMAIL = "adam.d.schueller@gmail.com"

setup(
    name=NAME,
    version=VERSION,
    license=LICENSE,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages("src"),
    package_data={"shoe_backtest": ["*.json"]},
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
)
