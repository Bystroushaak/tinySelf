



Compilation
-----------

You will need:

* mercurial
* pypy
* gcc
* python

Pypy with PIP
+++++++++++++

You can install pypy from your repositories. For example::

    sudo apt install pypy

PIP for pypy
++++++++++++

You will also need PIP configured to install packages into your pypy paths. Easiest way how to do it is to run the PIP install script::

    curl https://bootstrap.pypa.io/get-pip.py | pypy

rpython
+++++++

Get newest version of the rpython, which is part of the pypy project repository:

::

    hg clone https://bitbucket.org/pypy/pypy

(If you already have the repository cloned, just run ``hg pull``.)

rply
++++

Newest version of the rply (parser):

::

    pypy -m pip install --user -U git+https://github.com/alex/rply.git


requirements.txt
++++++++++++++++

Stuff from the ``requirements.txt``::

    pip install --user -r requirements.txt
