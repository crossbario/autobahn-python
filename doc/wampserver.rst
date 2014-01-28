Server
======

The classes :class:`autobahn.wamp1.protocol.WampServerProtocol` and
:class:`autobahn.wamp1.protocol.WampServerFactory` are the base classes
you derive from to implement WAMP servers.



Factory
-------

.. autoclass:: autobahn.wamp1.protocol.WampServerFactory
   :members: dispatch,
             sessionIdsToProtos,
             protosToSessionIds,
             startFactory,
             stopFactory


Protocol
--------

.. autoclass:: autobahn.wamp1.protocol.WampServerProtocol
   :members: onSessionOpen,
             dispatch,
             registerForRpc,
             registerMethodForRpc,
             registerProcedureForRpc,
             registerHandlerMethodForRpc,
             registerHandlerProcedureForRpc,
             registerForPubSub,
             registerHandlerForPubSub,
             registerHandlerForSub,
             registerHandlerForPub


.. autoclass:: autobahn.wamp1.protocol.WampCraServerProtocol
   :members: clientAuthTimeout,
             clientAuthAllowAnonymous,
             getAuthSecret,
             getAuthPermissions,
             onAuthenticated,
             onAuthTimeout,
             registerForPubSubFromPermissions
