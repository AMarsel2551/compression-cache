#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name="compression-cache",
    version="0.0.4",
    packages=find_packages(),
    description='Python function caching with compression',
    install_requires=["zstandard==0.23.0"],
    author_email="m.adbullinn@gmail.com",
    zip_safe=False,
    url="https://github.com/AMarsel2551/compression-cache.git"
)
