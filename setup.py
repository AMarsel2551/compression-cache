from setuptools import setup, find_packages


setup(
    name="Cache",
    version="0.1.0",  
    author="Marsel",
    author_email="m.adbullinn@example.com",
    description="...",
    long_description="",
    long_description_content_type="text/markdown",  
    url="https://github.com/AMarsel2551/cache.git",
    packages=find_packages(where="src"),  
    package_dir={"": "src"},  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  
    install_requires=[
        "zstandard==0.23.0",
    ],
    extras_require={
        "dev": [
            "zstandard==0.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "example-cli=example_library.cli:main",  
        ],
    },
    include_package_data=True,  
    license="MIT",  
)
