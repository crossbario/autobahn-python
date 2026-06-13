Installation
============

This document describes the prerequisites and the installation of |Ab|.

Requirements
------------

|ab| runs on Python on top of these networking frameworks:

* `Twisted`_
* `asyncio`_

|ab| requires Python 3.11 or later. You will need at least one of the
networking frameworks above.

.. note::
   Most of Autobahn's WebSocket and WAMP features are available on both Twisted and asyncio, so you are free to choose the underlying networking framework based on your own criteria.

For Twisted installation, please see `here <http://twistedmatrix.com/>`__.
Asyncio is included in the Python standard library for all supported
Python versions.


Supported Configurations
........................

Here are the configurations supported by |ab|:

.. list-table::
   :header-rows: 1

   * - Python
     - Twisted
     - asyncio
     - Notes
   * - CPython 3.11, 3.12, 3.13, and 3.14
     - yes
     - yes
     - Pre-built wheels are published for supported platforms.
   * - PyPy 3.11
     - yes
     - yes
     - Pre-built wheels are published for supported platforms.


Performance Note
................

|ab| is portable, well tuned code. For best performance, use the
pre-built wheels published on PyPI when one is available for your Python
version and platform. Platform-specific wheels may include native CFFI
and NVX acceleration; the source distribution remains available for
unsupported wheel combinations. See :doc:`wheels-inventory` for the full
wheel matrix.

To give you an idea of the performance you can expect, here is a `blog post <http://crossbario.com/blog/post/autobahn-pi-benchmark/>`_ benchmarking |ab| running on the `RaspberryPi <http://www.raspberrypi.org/>`_ (a tiny embedded computer) under `PyPy <http://pypy.org/>`_.



Installing Autobahn
-------------------


Using Docker
............

We offer `Docker Images <https://hub.docker.com/r/crossbario/autobahn-python/>`_ with |ab| pre-installed. To use this, if you have Docker already installed, just do

   ``sudo docker run -it crossbario/autobahn-python python client.py --url ws://IP _of_WAMP_router:8080/ws --realm realm1``

This starts up a Docker container and `client.py`, which connects to a Crossbar.io router at the given URL and to the given realm.

There are several docker images to choose from, depending on whether you are using CPython or PyPy.

There are the flavors which are based on the official CPython and PyPy images, plus versions using Alpine Linux, which have a smaller footprint. (Note: Footprint only matters for the download once per machine, after that the cached image is used. Containers off the same image/layers only take up space corresponding to how different from the image they are, so image size is relatively less important when using multiple containers.)


Install from PyPI
.................

To install |ab| from the `Python Package Index <http://pypi.python.org/pypi/autobahn>`_
using `Pip <http://www.pip-installer.org/en/latest/installing.html>`_:

.. code-block:: sh

   python -m pip install --upgrade pip
   python -m pip install autobahn

This is the recommended installation method. Pip will select a
pre-built wheel when one matches your Python implementation, Python
version, operating system, and CPU architecture. Current releases publish
wheels for CPython 3.11 through 3.14 and PyPy 3.11 across the supported
Linux, macOS, and Windows targets documented in :doc:`wheels-inventory`.

You can also specify *install variants* (see below). E.g. to install Twisted automatically as a dependency

.. code-block:: sh

   python -m pip install "autobahn[twisted]"

No extra is needed for asyncio because it is included in the Python
standard library.


Install from Sources
....................

To install from sources, clone the repository:

.. code-block:: sh

   git clone git@github.com:crossbario/autobahn-python.git

checkout a tagged release:

.. code-block:: sh

   cd autobahn-python
   git checkout v25.12.2

.. warning::
   You should only use *tagged* releases, not *master*. The latest code from *master* might be broken, unfinished and untested. So you have been warned ;)

Then install the checkout:

.. code-block:: sh

   python -m pip install -e ".[twisted]"


Install Variants
................

|Ab| has the following install variants:

.. list-table::
   :header-rows: 1

   * - Variant
     - Description
   * - ``twisted``
     - Install Twisted as a dependency.
   * - ``asyncio``
     - Backwards-compatible no-op; asyncio is in the Python standard library.
   * - ``accelerate``
     - Backwards-compatible no-op; native acceleration is provided by Autobahn wheels where supported.
   * - ``compress``
     - Install packages for non-standard WebSocket compression methods.
   * - ``encryption``
     - Install TLS and WAMP encryption/authentication packages.
   * - ``scram``
     - Install WAMP-SCRAM authentication packages.
   * - ``serialization``
     - Install ``bjdata`` to enable the optional UBJSON WAMP serializer. CPython-only - it cannot install on PyPy (upstream ``NeuroJSON/pybj#6``); on CPython without a compiler set ``PYBJDATA_NO_EXTENSION=1`` for a pure-Python build. JSON, MessagePack, CBOR and FlatBuffers are always available without this extra (use them on PyPy).
   * - ``nvx``
     - Backwards-compatible no-op; NVX acceleration is included in binary wheels where supported.
   * - ``all``
     - Install all optional feature dependencies.

Install variants can be combined, e.g. to install |ab| with all optional packages for use with Twisted on CPython:

.. code-block:: sh

   python -m pip install "autobahn[twisted,compress,encryption,scram]"


Windows Installation
....................

For convenience, here are minimal instructions to install both Python and Autobahn/Twisted on Windows:

1. Go to the `Python web site <https://www.python.org/downloads/>`_ and install a supported 64-bit Python 3.11 or later release.
2. Ensure Python and ``Scripts`` are available on your ``PATH``.
3. Download the `Pip install script <https://bootstrap.pypa.io/get-pip.py>`_ and double click it (or run ``python get-pip.py`` from a command shell)
4. Open a command shell and run ``python -m pip install "autobahn[twisted]"``.


Check the Installation
----------------------

To check the installation, fire up the Python and run

.. doctest::

   >>> from autobahn import __version__
   >>> print(__version__)
   25.12.2


Depending on Autobahn
---------------------

To require |Ab| as a dependency of your package, include the following in your ``setup.py`` script

.. code-block:: python

   install_requires = ["autobahn>=25.12.2"]

You can also depend on an *install variant* which automatically installs dependent packages

.. code-block:: python

   install_requires = ["autobahn[twisted]>=25.12.2"]

The latter will automatically install Twisted as a dependency.

-------

*Where to go*

Now you've got |Ab| installed, depending on your needs, head over to

* :doc:`asynchronous-programming` - An very short introduction plus pointers to good Web resources.
* :doc:`websocket/programming` - A guide to programming WebSocket applications with |ab|
* :doc:`wamp/programming` - A guide to programming WAMP applications with |ab|
