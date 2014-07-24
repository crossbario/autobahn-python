
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



There are many more examples showing options and advanced features:

* :doc:`WebSocket Examples <websocket/examples>`.
* :doc:`WAMP Examples <wamp/examples>`.


.. note::

   * WAMP application components can be run in servers and clients without any modification to your component class.

   * `AutobahnJS`_ allows you to write WAMP application components in JavaScript which run in browsers and Nodejs. Here is how above example `looks like <https://github.com/tavendo/AutobahnJS/#show-me-some-code>`_ in JavaScript.

