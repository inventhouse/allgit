# Copyright (c) 2021 Benjamin Holt -- MIT License

from setuptools import setup

from allgit import _version
#####


#####
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="allgit",
    version=_version,
    description="""Powerful "git multiplexer" for easily working with many repositories""",
    long_description=long_description,  # FIXME: Do something better than just dumping the whole readme
    long_description_content_type="text/markdown",
    url="https://github.com/inventhouse/allgit",
    author="Benjamin Holt",
    license="MIT",
    py_modules=["allgit"],
    entry_points={
        "console_scripts": [
            "allgit=allgit:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Version Control",
    ],
    keywords="git",
)
#####
