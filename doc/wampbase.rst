Base
====

The classes :class:`autobahn.wamp1.protocol.WampProtocol` and
:class:`autobahn.wamp1.protocol.WampFactory` are additional base classes ("mixins")
for the WAMP client and server classes. They contain functionality
common to both client and server roles.


Factory
-------

.. autoclass:: autobahn.wamp1.protocol.WampFactory



Protocol
--------

.. autoclass:: autobahn.wamp1.protocol.WampProtocol
   :members: URI_WAMP_BASE,
             URI_WAMP_PROCEDURE,
             URI_WAMP_TOPIC,
             URI_WAMP_ERROR,
             URI_WAMP_ERROR_GENERIC,
             URI_WAMP_ERROR_INTERNAL,
             shrink,
             resolve

.. autoclass:: autobahn.wamp1.protocol.WampCraProtocol
   :members: authSignature
