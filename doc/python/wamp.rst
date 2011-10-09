Autobahn WebSockets RPC/PubSub
==============================

RPC/PubSub Servers
------------------

The classes :class:`autobahn.wamp.WampServerProtocol` and
:class:`autobahn.wamp.WampServerFactory` are the base classes
you derive from to implement Autobahn WebSockets RPC/PubSub servers.


.. autoclass:: autobahn.wamp.WampServerProtocol
   :members: registerForRpc,
             registerMethodForRpc,
             registerProcedureForRpc

.. autoclass:: autobahn.wamp.WampServerFactory


RPC/PubSub Clients
------------------

The classes :class:`autobahn.wamp.WampClientProtocol` and
:class:`autobahn.wamp.WampClientFactory` are the base classes
you derive from to implement Autobahn WebSockets RPC/PubSub clients.


.. autoclass:: autobahn.wamp.WampClientProtocol
   :members: prefix,
             call,
             subscribe,
             unsubscribe,
             publish

.. autoclass:: autobahn.wamp.WampClientFactory



RPC/PubSub Protocol
-------------------

.. autoclass:: autobahn.wamp.WampProtocol
   :members: MESSAGE_TYPEID_NULL,
             MESSAGE_TYPEID_PREFIX,
             MESSAGE_TYPEID_CALL,
             MESSAGE_TYPEID_CALL_RESULT,
             MESSAGE_TYPEID_CALL_ERROR,
             MESSAGE_TYPEID_SUBSCRIBE,
             MESSAGE_TYPEID_UNSUBSCRIBE,
             MESSAGE_TYPEID_PUBLISH,
             MESSAGE_TYPEID_EVENT,
             shrinkUri,
             resolveCurie,
             resolveCurieOrPass
