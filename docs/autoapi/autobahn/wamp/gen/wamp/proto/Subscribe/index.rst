:mod:`autobahn.wamp.gen.wamp.proto.Subscribe`
=============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Subscribe


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Subscribe.Subscribe



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Subscribe.SubscribeStart
   autobahn.wamp.gen.wamp.proto.Subscribe.SubscribeAddRequest
   autobahn.wamp.gen.wamp.proto.Subscribe.SubscribeAddTopic
   autobahn.wamp.gen.wamp.proto.Subscribe.SubscribeAddMatch
   autobahn.wamp.gen.wamp.proto.Subscribe.SubscribeAddGetRetained
   autobahn.wamp.gen.wamp.proto.Subscribe.SubscribeEnd


.. class:: Subscribe

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsSubscribe(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Topic(self)


   .. method:: Match(self)


   .. method:: GetRetained(self)



.. function:: SubscribeStart(builder)


.. function:: SubscribeAddRequest(builder, request)


.. function:: SubscribeAddTopic(builder, topic)


.. function:: SubscribeAddMatch(builder, match)


.. function:: SubscribeAddGetRetained(builder, getRetained)


.. function:: SubscribeEnd(builder)


