WAMP Interfaces
===============

Core Interfaces
---------------

WAMP application components are implemented by deriving from the class :class:`autobahn.wamp.protocol.ApplicationSession`. This class implements the following core interfaces for WAMP application programming:

 * :class:`autobahn.wamp.interfaces.ISession`
 * :class:`autobahn.wamp.interfaces.ICaller`
 * :class:`autobahn.wamp.interfaces.ICallee`
 * :class:`autobahn.wamp.interfaces.IPublisher`
 * :class:`autobahn.wamp.interfaces.ISubscriber`

====


Sessions
++++++++

Base interface for WAMP sessions of any role:

.. autoclass:: autobahn.wamp.interfaces.ISession
   :members:


Session Details
^^^^^^^^^^^^^^^

When a WAMP session is open, details on the session are provided by this object:

.. autoclass:: autobahn.wamp.types.SessionDetails
   :show-inheritance:
   :members: __init__


Close Details
^^^^^^^^^^^^^

When a WAMP session is to be closed, this object can provide closing details:

.. autoclass:: autobahn.wamp.types.CloseDetails
   :show-inheritance:
   :members: __init__

====


Callers
+++++++


Calling
^^^^^^^

*Callers* can call remote procedures on other WAMP application components using the following interface:

.. autoclass:: autobahn.wamp.interfaces.ICaller
   :members:


Call Options
^^^^^^^^^^^^

To set options when issuing a call, provide a keyword argument ``options`` of the following type to :func:`autobahn.wamp.interfaces.ICaller.call`:

.. autoclass:: autobahn.wamp.types.CallOptions
   :show-inheritance:
   :members: __init__


Call Results
^^^^^^^^^^^^

If a call result contains multiple positional result value and/or the call result contains keyword result values, the result is wrapped into an instance of:

.. autoclass:: autobahn.wamp.types.CallResult
   :show-inheritance:
   :members: __init__

====


Callees
+++++++

Registering
^^^^^^^^^^^

*Callees* provide endpoints which can be called as remote procedures from other WAMP application components:

.. autoclass:: autobahn.wamp.interfaces.ICallee
   :members:


Registration
^^^^^^^^^^^^

Each registration of an endpoint at a *Dealer* is represented by

.. autoclass:: autobahn.wamp.interfaces.IRegistration
   :members:


Register Options
^^^^^^^^^^^^^^^^

.. autoclass:: autobahn.wamp.types.RegisterOptions
   :show-inheritance:
   :members: __init__


Call Details
^^^^^^^^^^^^

.. autoclass:: autobahn.wamp.types.CallDetails
   :show-inheritance:
   :members: __init__

====


Subscribers
+++++++++++

Subscribing
^^^^^^^^^^^

.. autoclass:: autobahn.wamp.interfaces.ISubscriber
   :members:


Subscription
^^^^^^^^^^^^

.. autoclass:: autobahn.wamp.interfaces.ISubscription
   :members:


Subscribe Options
^^^^^^^^^^^^^^^^^

.. autoclass:: autobahn.wamp.types.SubscribeOptions
   :show-inheritance:
   :members: __init__


Event Details
^^^^^^^^^^^^^

.. autoclass:: autobahn.wamp.types.EventDetails
   :show-inheritance:
   :members: __init__

====



Publishers
++++++++++

Publishing
^^^^^^^^^^

.. autoclass:: autobahn.wamp.interfaces.IPublisher
   :members:


Publication
^^^^^^^^^^^

.. autoclass:: autobahn.wamp.interfaces.IPublication
   :members:


Publish Options
^^^^^^^^^^^^^^^

.. autoclass:: autobahn.wamp.types.PublishOptions
   :show-inheritance:
   :members: __init__

====



Decorators
++++++++++

.. autofunction:: autobahn.wamp.register

.. autofunction:: autobahn.wamp.subscribe

.. autofunction:: autobahn.wamp.error



Other Interfaces
----------------

.. autoclass:: autobahn.wamp.interfaces.IObjectSerializer
   :members:

.. autoclass:: autobahn.wamp.interfaces.IMessage
   :members:

.. autoclass:: autobahn.wamp.interfaces.ISerializer
   :members:

.. autoclass:: autobahn.wamp.interfaces.ITransport
   :members:

.. autoclass:: autobahn.wamp.interfaces.ITransportHandler
   :members:

.. autoclass:: autobahn.wamp.interfaces.IRouterBase
   :members:

.. autoclass:: autobahn.wamp.interfaces.IRouter
   :members:

.. autoclass:: autobahn.wamp.interfaces.IBroker
   :members:

.. autoclass:: autobahn.wamp.interfaces.IDealer
   :members:

.. autoclass:: autobahn.wamp.interfaces.IRouterFactory
   :members:
