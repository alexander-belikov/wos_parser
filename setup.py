import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="wos_parser",
    version="1.0",
    author="Alexander Belikov",
    author_email="abelikov@gmail.com",
    description="tools for parsing xmls of web of science data",
    license="BSD",
    keywords="xml",
    url="git@github.com:alexander-belikov/wos_parser.git",
    packages=['wos_parser'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 0 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
        'lxml', 'Cython'
    ]
)
