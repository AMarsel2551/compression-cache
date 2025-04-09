#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup


PROJECT_URL = "https://github.com/AMarsel2551/compression-cache"


def read_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()


def read_requirements():
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), encoding='utf-8') as f:
        return f.read().splitlines()


setup(
    name="compression-cache",
    version="0.0.12",
    packages=find_packages(),
    description='Python function caching with compression',
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    install_requires=read_requirements(),
    author_email="m.adbullinn@gmail.com",
    zip_safe=False,
    url=PROJECT_URL,
    project_urls={
        "Source Code": PROJECT_URL + ".git",
        "Documentation": PROJECT_URL + "/wiki",
    },
)
