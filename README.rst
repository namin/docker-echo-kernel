docker-echo-kernel
==================

demo_

.. _demo : http://jupyter.livecode.ch:7777/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fnamin%2Fdocker-echo-kernel&branch=master&urlpath=tree%2Fdocker-echo-kernel%2Fnotebooks%2Fsample.ipynb

based on echo_kernel
====================

``echo_kernel`` is a simple example of a Jupyter kernel. This repository
complements the documentation on wrapper kernels here:

http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html

Installation
------------
To install ``echo_kernel`` from PyPI::

    pip install echo_kernel
    python -m echo_kernel.install

Using the Echo kernel
---------------------
**Notebook**: The *New* menu in the notebook should show an option for an Echo notebook.

**Console frontends**: To use it with the console frontends, add ``--kernel echo`` to
their command line arguments.
