.. image:: https://github.com/alexander-belikov/wos_parser/extras/wos_parser_logo.jpg?raw=true
    :alt: WoS parser logo
    :align: center

WoS parser is a Python package for parsing the Web of Science XML data

Features
--------

-  Intuitive model specification syntax, for example, ``x ~ N(0,1)``
-  **Variational inference**: `ADVI <http://arxiv.org/abs/1506.03431>`__
   for fast approximate posterior estimation as well as mini-batch ADVI
   for large data sets.
-  Relies on `Theano <http://deeplearning.net/software/theano/>`__ which provides:
    *  Computation optimization and dynamic C compilation
    *  Numpy broadcasting and advanced indexing
    *  Linear algebra operators
    *  Simple extensibility

NB
---------------

-  The external scripts in provide examples of how to use the parser. The first use case of WoS parser was to run it on AWS-based `Cloud Kotta <https://github.com/yadudoc/cloud_kotta>` system using `Kotta client <https://github.com/yadudoc/kotta_client>`.
    * ``enter_kotta_wos.py`` is an example of the job submission from the client side. NB: it was originally run in an interactive shell and does not account for the time of the actual compute (i.e. it is only provided as an example
    * ``runner.sh`` is the actual script used for running parser jobs.


Installation
------------

To install clone the repository and use
``python setup.py install`` or ``python setup.py develop``.

