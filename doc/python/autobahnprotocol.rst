Autobahn RPC/PubSub
===================

Autobahn RPC/PubSub Servers
---------------------------

The classes :class:`autobahn.autobahn.AutobahnServerProtocol` and
:class:`autobahn.autobahn.AutobahnServerFactory` are the base classes
you derive from to implement Autobahn RPC/PubSub servers.


.. autoclass:: autobahn.autobahn.AutobahnServerProtocol
   :members: registerForRpc,
             registerMethodForRpc,
             registerProcedureForRpc,
             publish

.. autoclass:: autobahn.autobahn.AutobahnServerFactory


Autobahn RPC/PubSub Clients
---------------------------

The classes :class:`autobahn.autobahn.AutobahnClientProtocol` and
:class:`autobahn.autobahn.AutobahnClientFactory` are the base classes
you derive from to implement Autobahn RPC/PubSub clients.


.. autoclass:: autobahn.autobahn.AutobahnClientProtocol
   :members: call, subscribe, unsubscribe, publish

.. autoclass:: autobahn.autobahn.AutobahnClientFactory



Autobahn RPC/PubSub Protocol
----------------------------

.. autoclass:: autobahn.autobahn.AutobahnProtocol
   :members: MESSAGE_TYPEID_CALL,
             MESSAGE_TYPEID_SUBSCRIBE,
             MESSAGE_TYPEID_UNSUBSCRIBE,
             MESSAGE_TYPEID_PUBLISH,
             MESSAGE_TYPEID_CALL_RESULT,
             MESSAGE_TYPEID_CALL_ERROR,
             MESSAGE_TYPEID_EVENT
