from setuptools import find_packages, setup

setup(
    name="Cache",
    version="0.1.2",
    packages=find_packages(),
    install_requires=["zstandard==0.23.0"],
)
