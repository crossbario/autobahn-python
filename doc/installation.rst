Installation
============

This document describes the prerequisites and the installation of |Ab|.

Requirements
------------

|ab| runs on Python on top of these networking frameworks:

* `Twisted`_
* `asyncio`_

You will need at least one of those.

.. note::
   Most of Autobahn's WebSocket and WAMP features are available on both Twisted and asyncio, so you are free to choose the underlying networking framework based on your own criteria.

For Twisted installation, please see `here <http://twistedmatrix.com/>`__. Asyncio comes bundled with Python 3.4+. For Python 3.3, install it from `here <https://pypi.python.org/pypi/asyncio>`__. For Python 2, `trollius`_ will work.


Supported Configurations
........................

Here are the configurations supported by |ab|:

+---------------+-----------+---------+---------------------------------+
| Python        | Twisted   | asyncio | Notes                           |
+---------------+-----------+---------+---------------------------------+
| CPython 2.7   | yes       | yes     | asyncio support via `trollius`_ |
+---------------+-----------+---------+---------------------------------+
| CPython 3.3   | yes       | yes     | asyncio support via `tulip`_    |
+---------------+-----------+---------+---------------------------------+
| CPython 3.4+  | yes       | yes     | asyncio in the standard library |
+---------------+-----------+---------+---------------------------------+
| PyPy 2.2+     | yes       | yes     | asyncio support via `trollius`_ |
+---------------+-----------+---------+---------------------------------+
| Jython 2.7+   | yes       | ?       | Issues: `1`_, `2`_              |
+---------------+-----------+---------+---------------------------------+

.. _1: http://twistedmatrix.com/trac/ticket/3413
.. _2: http://twistedmatrix.com/trac/ticket/6746


Performance Note
................

|ab| is portable, well tuned code. You can further accelerate performance by

* Running under `PyPy <http://pypy.org/>`_ (recommended!) or
* on CPython, install the native accelerators `wsaccel <https://pypi.python.org/pypi/wsaccel/>`_ and `ujson <https://pypi.python.org/pypi/ujson/>`_ (you can use the install variant ``acceleration`` for that - see below)

To give you an idea of the performance you can expect, here is a `blog post <http://crossbario.com/blog/post/autobahn-pi-benchmark/>`_ benchmarking |ab| running on the `RaspberryPi <http://www.raspberrypi.org/>`_ (a tiny embedded computer) under `PyPy <http://pypy.org/>`_.



Installing Autobahn
-------------------


Using Docker
............

We offer `Docker Images <https://hub.docker.com/r/crossbario/autobahn-python/>`_ with |ab| pre-installed. To use this, if you have Docker already installed, just do

   ``sudo docker run -it crossbario/autobahn-python:cpy2 python client.py --url ws://IP _of_WAMP_router:8080/ws --realm realm1``

This starts up a Docker container and `client.py`, which connects to a Crossbar.io router at the given URL and to the given realm.

There are several docker images to choose from, depending on whether you are using Python 2, 3 or PyPy (Python 2 only for now).

There are the flavors which are based on the official Python 2, 3 and PyPy images, plus Python 2 and 3 versions using Alpine Linux, which have a smaller footprint. (Note: Footprint only matters for the download once per machine, after that the cached image is used. Containers off the same image/layers only take up space corresponding to how different from the image they are, so image size is relatively less important when using multiple containers.)


Install from PyPI
.................

To install |ab| from the `Python Package Index <http://pypi.python.org/pypi/autobahn>`_ using `Pip <http://www.pip-installer.org/en/latest/installing.html>`_

.. code-block:: sh

   pip install autobahn

You can also specify *install variants* (see below). E.g. to install Twisted automatically as a dependency

.. code-block:: sh

   pip install autobahn[twisted]

And to install asyncio backports automatically when required

.. code-block:: sh

   pip install autobahn[asyncio]


Install from Sources
....................

To install from sources, clone the repository:

.. code-block:: sh

   git clone git@github.com:crossbario/autobahn-python.git

checkout a tagged release:

.. code-block:: sh

   cd AutobahnPython
   git checkout v0.9.1

.. warning::
   You should only use *tagged* releases, not *master*. The latest code from *master* might be broken, unfinished and untested. So you have been warned ;)

Then do:

.. code-block:: sh

   cd autobahn
   python setup.py install

You can also use ``pip`` for the last step, which allows to specify install variants (see below)

.. code-block:: sh

   pip install -e .[twisted]


Install Variants
................

|Ab| has the following install variants:

+-------------------+--------------------------------------------------------------------------------------------------------+
| **Variant**       | **Description**                                                                                        |
+-------------------+--------------------------------------------------------------------------------------------------------+
| ``twisted``       | Install Twisted as a dependency                                                                        |
+-------------------+--------------------------------------------------------------------------------------------------------+
| ``asyncio``       | Install asyncio as a dependency (or use stdlib)                                                        |
+-------------------+--------------------------------------------------------------------------------------------------------+
| ``accelerate``    | Install native acceleration packages on CPython                                                        |
+-------------------+--------------------------------------------------------------------------------------------------------+
| ``compress``      | Install packages for non-standard WebSocket compression methods                                        |
+-------------------+--------------------------------------------------------------------------------------------------------+
| ``serialization`` | Install packages for additional WAMP serialization formats (currently `MsgPack <http://msgpack.org>`_) |
+-------------------+--------------------------------------------------------------------------------------------------------+

Install variants can be combined, e.g. to install |ab| with all optional packages for use with Twisted on CPython:

.. code-block:: sh

   pip install autobahn[twisted,accelerate,compress,serialization]


Windows Installation
....................

For convenience, here are minimal instructions to install both Python and Autobahn/Twisted on Windows:

1. Go to the `Python web site <https://www.python.org/downloads/>`_ and install Python 2.7 32-Bit
2. Add ``C:\Python27;C:\Python27\Scripts;`` to your ``PATH``
3. Download the `Pip install script <https://bootstrap.pypa.io/get-pip.py>`_ and double click it (or run ``python get-pip.py`` from a command shell)
4. Open a command shell and run ``pip install autobahn[twisted]``


Check the Installation
----------------------

To check the installation, fire up the Python and run

.. doctest::

   >>> from autobahn import __version__
   >>> print(__version__)
   0.9.1


Depending on Autobahn
---------------------

To require |Ab| as a dependency of your package, include the following in your ``setup.py`` script

.. code-block:: python

   install_requires = ["autobahn>=0.9.1"]

You can also depend on an *install variant* which automatically installs dependent packages

.. code-block:: python

   install_requires = ["autobahn[twisted]>=0.9.1"]

The latter will automatically install Twisted as a dependency.

-------

*Where to go*

Now you've got |Ab| installed, depending on your needs, head over to

* :doc:`asynchronous-programming` - An very short introduction plus pointers to good Web resources.
* :doc:`websocket/programming` - A guide to programming WebSocket applications with |ab|
* :doc:`wamp/programming` - A guide to programming WAMP applications with |ab|
