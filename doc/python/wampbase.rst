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
   :members: shrink,
             resolve
