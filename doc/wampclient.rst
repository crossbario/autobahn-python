Client
======

The classes :class:`autobahn.wamp.WampClientProtocol` and
:class:`autobahn.wamp.WampClientFactory` are the base classes
you derive from to implement WAMP clients.



Factory
-------

.. autoclass:: autobahn.wamp.WampClientFactory
   :members: startFactory,
             stopFactory



Protocol
--------

.. autoclass:: autobahn.wamp.WampClientProtocol
   :members: onSessionOpen,
             prefix,
             call,
             publish,
             subscribe,
             unsubscribe


.. autoclass:: autobahn.wamp.WampCraClientProtocol
   :members: authenticate
