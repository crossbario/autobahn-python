Installation
============

Requirements
------------

You will need at least one of Twisted or Asyncio as your networking framework.

..note:: Asyncio comes bundled with Python 3.4. For Python 3.3, install it from `here <https://pypi.python.org/pypi/asyncio>`_. For Twisted, please see `here <http://twistedmatrix.com/>`_.


Install from Python Package Index
---------------------------------

Install from the `Python Package Index <http://pypi.python.org/pypi/autobahn>`_ using `Pip <http://www.pip-installer.org/en/latest/installing.html>`_:

::

   pip install autobahn

You can also specify install variants

::

   pip install autobahn[twisted,accelerate]

The latter will automatically install Twisted and native acceleration packages when running on CPython.

::

   pip install autobahn[asyncio,accelerate]

The latter will automatically install asyncio backports when required and native acceleration packages when running on CPython.


Install from Sources
--------------------

To install from sources, clone the repo

::

   git clone git@github.com:tavendo/AutobahnPython.git

checkout a tagged release

::

   cd AutobahnPython
   git checkout v0.8.5

and install

::

   cd autobahn
   python setup.py install

You can also use Pip for the last step, which allows to specify install variants

::

   pip install -e .[twisted]

|ab| has the following install variants:

 1. ``twisted``: Install Twisted as a dependency
 2. ``asyncio``: Install asyncio backports when required
 3. ``accelerate``: Install native acceleration packages on CPython
 4. ``compress``: Install packages for non-standard WebSocket compression methods
 5. ``serialization``: Install packages for additional WAMP serialization formats (currently [MsgPack](http://msgpack.org/))


Performance
-----------

|ab| is portable, well tuned code. You can further accelerate performance by

 * Running under `PyPy <http://pypy.org/>`_ or
 * on CPython, install the native accelerators `wsaccel <https://pypi.python.org/pypi/wsaccel/>`_ and `ujson <https://pypi.python.org/pypi/ujson/>`_ (you can use the install variant ``acceleration`` for that)


Depending on Autobahn
---------------------

To require |ab| as a dependency of your package, include the following in your ``setup.py``:

::

   install_requires = ["autobahn>=0.7.2"]

You can also depend on an install variant which automatically installs respective packages:

::

   install_requires = ["autobahn[twisted,accelerate]>=0.7.2"]


Check the installation
----------------------

In the Python interpreter, to check the installation do:

.. doctest::

   >>> from autobahn import __version__
   >>> print(__version__)
   0.8.5
