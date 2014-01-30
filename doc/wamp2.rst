WAMP v2
=======

Interfaces
----------

.. autointerface:: autobahn.wamp.interfaces.IObjectSerializer
   :members:

.. autointerface:: autobahn.wamp.interfaces.IMessage
   :members:

.. autointerface:: autobahn.wamp.interfaces.ISerializer
   :members:

.. autointerface:: autobahn.wamp.interfaces.ITransport
   :members:

.. autointerface:: autobahn.wamp.interfaces.ITransportHandler
   :members:

.. autointerface:: autobahn.wamp.interfaces.ISession
   :members:

.. autointerface:: autobahn.wamp.interfaces.ICaller
   :members:

.. autointerface:: autobahn.wamp.interfaces.ICallee
   :members:

.. autointerface:: autobahn.wamp.interfaces.IPublisher
   :members:

.. autointerface:: autobahn.wamp.interfaces.ISubscriber
   :members:

.. autointerface:: autobahn.wamp.interfaces.IRouter
   :members:

.. autointerface:: autobahn.wamp.interfaces.IBroker
   :members:

.. autointerface:: autobahn.wamp.interfaces.IDealer
   :members:


Errors
------

.. autoclass:: autobahn.wamp.exception.Error
   :show-inheritance:
   :members: __init__

.. autoclass:: autobahn.wamp.exception.SessionNotReady
   :show-inheritance:
   :members: __init__

.. autoclass:: autobahn.wamp.exception.ProtocolError
   :show-inheritance:
   :members: __init__

.. autoclass:: autobahn.wamp.exception.TransportLost
   :show-inheritance:
   :members: __init__

.. autoclass:: autobahn.wamp.exception.ApplicationError
   :show-inheritance:
   :members: __init__

.. autoclass:: autobahn.wamp.exception.NotAuthorized
   :show-inheritance:
   :members: __init__

.. autoclass:: autobahn.wamp.exception.InvalidTopic
   :show-inheritance:
   :members: __init__

.. autoclass:: autobahn.wamp.exception.CallError
   :show-inheritance:
   :members: __init__

.. autoclass:: autobahn.wamp.exception.CanceledError
   :show-inheritance:
   :members: __init__


Router
------

.. autoclass:: autobahn.wamp.broker.Broker
   :show-inheritance:
   :members: __init__,
             addSession,
             removeSession,
             processMessage

.. autoclass:: autobahn.wamp.dealer.Dealer
   :show-inheritance:
   :members: __init__,
             addSession,
             removeSession,
             processMessage


Protocol
--------

.. autoclass:: autobahn.wamp.protocol.Publication
   :show-inheritance:
   :members: __init__


.. autoclass:: autobahn.wamp.protocol.Subscription
   :show-inheritance:
   :members: __init__,
             unsubscribe


.. autoclass:: autobahn.wamp.protocol.Registration
   :show-inheritance:
   :members: __init__,
             unregister


.. autoclass:: autobahn.wamp.protocol.WampBaseSession
   :show-inheritance:
   :members: define


.. autoclass:: autobahn.wamp.protocol.WampAppSession
   :show-inheritance:
   :members: __init__,
             onOpen,
             onMessage,
             onClose,
             onSessionOpen,
             onSessionClose,
             closeSession,
             publish,
             subscribe,
             unsubscribe,
             call,
             register,
             unregister


.. autoclass:: autobahn.wamp.protocol.WampAppFactory
   :show-inheritance:
   :members: __call__


.. autoclass:: autobahn.wamp.protocol.WampRouterAppSession
   :show-inheritance:
   :members: __init__,
             send


.. autoclass:: autobahn.wamp.protocol.WampRouterSession
   :show-inheritance:


.. autoclass:: autobahn.wamp.protocol.WampRouterFactory
   :show-inheritance:
   :members: __init__,
             add,
             __call__


Types
-----

.. autoclass:: autobahn.wamp.types.SessionDetails
   :show-inheritance:
   :members: __init__


.. autoclass:: autobahn.wamp.types.CloseDetails
   :show-inheritance:
   :members: __init__


.. autoclass:: autobahn.wamp.types.SubscribeOptions
   :show-inheritance:
   :members: __init__


.. autoclass:: autobahn.wamp.types.EventDetails
   :show-inheritance:
   :members: __init__


.. autoclass:: autobahn.wamp.types.PublishOptions
   :show-inheritance:
   :members: __init__


.. autoclass:: autobahn.wamp.types.RegisterOptions
   :show-inheritance:
   :members: __init__


.. autoclass:: autobahn.wamp.types.CallDetails
   :show-inheritance:
   :members: __init__


.. autoclass:: autobahn.wamp.types.CallOptions
   :show-inheritance:
   :members: __init__


.. autoclass:: autobahn.wamp.types.CallResult
   :show-inheritance:
   :members: __init__

