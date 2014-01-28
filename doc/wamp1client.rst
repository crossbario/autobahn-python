Client
======

The classes :class:`autobahn.wamp1.protocol.WampClientProtocol` and
:class:`autobahn.wamp1.protocol.WampClientFactory` are the base classes
you derive from to implement WAMP v1 clients.



Factory
-------

.. autoclass:: autobahn.wamp1.protocol.WampClientFactory
   :members: startFactory,
             stopFactory



Protocol
--------

.. autoclass:: autobahn.wamp1.protocol.WampClientProtocol
   :members: onSessionOpen,
             prefix,
             call,
             publish,
             subscribe,
             unsubscribe


.. autoclass:: autobahn.wamp1.protocol.WampCraClientProtocol
   :members: authenticate
