#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name="ecomcache",
    version="0.1.5",
    packages=find_packages(),
    install_requires=["zstandard==0.23.0"],
)
