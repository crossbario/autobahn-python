Base
====

The classes :class:`autobahn.wamp.WampProtocol` and
:class:`autobahn.wamp.WampFactory` are additional base classes ("mixins")
for the WAMP client and server classes. They contain functionality
common to both client and server roles.


Factory
-------

.. autoclass:: autobahn.wamp.WampFactory



Protocol
--------

.. autoclass:: autobahn.wamp.WampProtocol
   :members: URI_WAMP_BASE,
             URI_WAMP_PROCEDURE,
             URI_WAMP_TOPIC,
             URI_WAMP_ERROR,
             URI_WAMP_ERROR_GENERIC,
             URI_WAMP_ERROR_INTERNAL,
             shrink,
             resolve

.. autoclass:: autobahn.wamp.WampCraProtocol
   :members: authSignature
