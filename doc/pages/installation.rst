Installation
============

Requirements
------------

|ab| runs on Python on top of a networking framework, either


1. `Twisted`_ or
2. `asyncio`_

and most of Autobahn's WebSocket and WAMP features are available on both Twisted and asyncio.

For Twisted installation, please see `here <http://twistedmatrix.com/>`_. Asyncio comes bundled with Python 3.4+. For Python 3.3, install it from `here <https://pypi.python.org/pypi/asyncio>`_. For Python 2, `trollius`_ will work.

Here are the configurations suppored by |ab|:

+---------------+-----------+---------+---------------------------------+
| Python        | Twisted   | asyncio | Notes                           |
+---------------+-----------+---------+---------------------------------+
| CPython 2.6   | yes       | yes     | asyncio support via `trollius`_ |
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


Install from PyPI
-----------------

To install |ab| from the `Python Package Index <http://pypi.python.org/pypi/autobahn>`_ using `Pip <http://www.pip-installer.org/en/latest/installing.html>`_

::

   $ pip install autobahn

You can also specify *install variants* (see below). E.g. to install Twisted automatically as a dependency

::

   pip install autobahn[twisted]

And to install asyncio backports automatically when required

::

   pip install autobahn[asyncio]


Install from Sources
--------------------

To install from sources, clone the repo

::

   git clone git@github.com:tavendo/AutobahnPython.git

checkout a tagged release

::

   cd AutobahnPython
   git checkout v0.8.12

and install

::

   cd autobahn
   python setup.py install

You can also use Pip for the last step, which allows to specify install variants (see below)

::

   pip install -e .[twisted]


Install Variants
----------------

|ab| has the following install variants:

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

::

   pip install autobahn[twisted,accelerate,compress,serialization]


Check the Installation
----------------------

To check the installation, fire up the Python and run

.. doctest::

   >>> from autobahn import __version__
   >>> print(__version__)
   0.8.12
