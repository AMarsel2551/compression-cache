#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup


def read_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(
    name="compression-cache",
    version="0.0.4",
    packages=find_packages(),
    description='Python function caching with compression',
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    install_requires=["zstandard==0.23.0"],
    author_email="m.adbullinn@gmail.com",
    zip_safe=False,
    url="https://github.com/AMarsel2551/compression-cache.git"
)
