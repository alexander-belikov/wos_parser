.. image:: https://github.com/alexander-belikov/wos_parser/raw/master/extras/wos_parser.jpg?raw=true
    :alt: WoS parser logo
    :align: center

WoS parser is a Python package for parsing the Web of Science XML data

Installation
------------

To install clone the repository and use
``python setup.py install`` or ``python setup.py develop``.

Remarks
-------

The scripts in ``./external_scripts`` provide examples of how to use the parser. The first use case of WoS parser was to run it on AWS-based `Cloud Kotta <https://github.com/yadudoc/cloud_kotta>`_ system using `Kotta client <https://github.com/yadudoc/kotta_client>`_.

    - ``enter_kotta_wos.py`` is an example of the job submission from the client side. NB: it was originally run in an interactive shell and does not account for the time of the actual compute (i.e. it is only provided as an example
    - ``runner.sh`` is the actual script used for running parser jobs.

