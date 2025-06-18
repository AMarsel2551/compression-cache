#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup


PROJECT_URL = "https://github.com/AMarsel2551/compression-cache"
INSTALL_REQUIRES=[
    "zstandard==0.23.0",
    "redis==5.2.1",
    "pydantic==2.11.7",
    "ujson==5.10.0",
]

def read_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(
    name="compression-cache",
    version="0.0.22",
    packages=find_packages(),
    description='Python function caching with compression',
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    install_requires=INSTALL_REQUIRES,
    author_email="m.adbullinn@gmail.com",
    zip_safe=False,
    url=PROJECT_URL,
    project_urls={
        "Source Code": PROJECT_URL + ".git",
        "Documentation": PROJECT_URL + "/wiki",
    },
)
