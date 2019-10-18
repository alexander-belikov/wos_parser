import os
from setuptools import setup


long_description="""
tools for event based xml parsing of web of science data,
the output is accumulated and dumped in chunks,
according to the flow parsable record are placed in the good heap,
while non-parsable (with respect to an enforced schema) are placed in the bad heap.
It is used to run on AWS-based Cloud Kotta infrastucture, while jobs are submitted using Kotta client
"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


classifiers = [
               'Programming Language :: Python :: 3.6',
               'Operating System :: OS Independent',
               'Topic :: Utilities'
]

setup(
    name="wos_parser",
    version="1.0",
    author="Alexander Belikov",
    author_email="abelikov@gmail.com",
    description="tools for parsing xmls of the web of science data",
    license="BSD",
    keywords="xml",
    url="git@github.com:alexander-belikov/wos_parser.git",
    packages=['wos_parser'],
    long_description=long_description,
    classifiers=classifiers,
    install_requires=[
        'lxml'
    ]
)
