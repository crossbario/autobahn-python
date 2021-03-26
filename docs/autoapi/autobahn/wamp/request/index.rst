:mod:`autobahn.wamp.request`
============================

.. py:module:: autobahn.wamp.request


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.request.Publication
   autobahn.wamp.request.Subscription
   autobahn.wamp.request.Handler
   autobahn.wamp.request.Registration
   autobahn.wamp.request.Endpoint
   autobahn.wamp.request.PublishRequest
   autobahn.wamp.request.SubscribeRequest
   autobahn.wamp.request.UnsubscribeRequest
   autobahn.wamp.request.CallRequest
   autobahn.wamp.request.InvocationRequest
   autobahn.wamp.request.RegisterRequest
   autobahn.wamp.request.UnregisterRequest



.. class:: Publication(publication_id, was_encrypted)


   Bases: :class:`object`

   Object representing a publication (feedback from publishing an event when doing
   an acknowledged publish).

   .. attribute:: __slots__
      :annotation: = ['id', 'was_encrypted']

      

   .. method:: __str__(self)

      Return str(self).



.. class:: Subscription(subscription_id, topic, session, handler)


   Bases: :class:`object`

   Object representing a handler subscription.

   .. attribute:: __slots__
      :annotation: = ['id', 'topic', 'active', 'session', 'handler']

      

   .. method:: unsubscribe(self)

      Unsubscribe this subscription.


   .. method:: __str__(self)

      Return str(self).



.. class:: Handler(fn, obj=None, details_arg=None)


   Bases: :class:`object`

   Object representing an event handler attached to a subscription.

   .. attribute:: __slots__
      :annotation: = ['fn', 'obj', 'details_arg']

      


.. class:: Registration(session, registration_id, procedure, endpoint)


   Bases: :class:`object`

   Object representing a registration.

   .. attribute:: __slots__
      :annotation: = ['id', 'active', 'session', 'procedure', 'endpoint']

      

   .. method:: unregister(self)

      


.. class:: Endpoint(fn, obj=None, details_arg=None)


   Bases: :class:`object`

   Object representing an procedure endpoint attached to a registration.

   .. attribute:: __slots__
      :annotation: = ['fn', 'obj', 'details_arg']

      


.. class:: PublishRequest(request_id, on_reply, was_encrypted)


   Bases: :class:`autobahn.wamp.request.Request`

   Object representing an outstanding request to publish (acknowledged) an event.

   .. attribute:: __slots__
      :annotation: = was_encrypted

      


.. class:: SubscribeRequest(request_id, topic, on_reply, handler)


   Bases: :class:`autobahn.wamp.request.Request`

   Object representing an outstanding request to subscribe to a topic.

   .. attribute:: __slots__
      :annotation: = ['handler', 'topic']

      


.. class:: UnsubscribeRequest(request_id, on_reply, subscription_id)


   Bases: :class:`autobahn.wamp.request.Request`

   Object representing an outstanding request to unsubscribe a subscription.

   .. attribute:: __slots__
      :annotation: = ['subscription_id']

      


.. class:: CallRequest(request_id, procedure, on_reply, options)


   Bases: :class:`autobahn.wamp.request.Request`

   Object representing an outstanding request to call a procedure.

   .. attribute:: __slots__
      :annotation: = ['procedure', 'options']

      


.. class:: InvocationRequest(request_id, on_reply)


   Bases: :class:`autobahn.wamp.request.Request`

   Object representing an outstanding request to invoke an endpoint.


.. class:: RegisterRequest(request_id, on_reply, procedure, endpoint)


   Bases: :class:`autobahn.wamp.request.Request`

   Object representing an outstanding request to register a procedure.

   .. attribute:: __slots__
      :annotation: = ['procedure', 'endpoint']

      


.. class:: UnregisterRequest(request_id, on_reply, registration_id)


   Bases: :class:`autobahn.wamp.request.Request`

   Object representing an outstanding request to unregister a registration.

   .. attribute:: __slots__
      :annotation: = ['registration_id']

      


