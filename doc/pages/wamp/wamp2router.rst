WAMP Router
===========

.. autoclass:: autobahn.wamp.broker.Broker
   :show-inheritance:
   :members: __init__,
             attach,
             detach,
             processPublish,
             processSubscribe,
             processUnsubscribe

.. autoclass:: autobahn.wamp.dealer.Dealer
   :show-inheritance:
   :members: __init__,
             attach,
             detach,
             processRegister,
             processUnregister,
             processCall,
             processCancel,
             processYield,
             processInvocationError
