from setuptools import setup, find_packages


setup(
    name="Cache",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "zstandard==0.23.0",
    ],
)
