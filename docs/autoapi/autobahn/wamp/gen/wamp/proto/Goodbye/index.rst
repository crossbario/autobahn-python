:mod:`autobahn.wamp.gen.wamp.proto.Goodbye`
===========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Goodbye


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Goodbye.Goodbye



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Goodbye.GoodbyeStart
   autobahn.wamp.gen.wamp.proto.Goodbye.GoodbyeAddReason
   autobahn.wamp.gen.wamp.proto.Goodbye.GoodbyeAddMessage
   autobahn.wamp.gen.wamp.proto.Goodbye.GoodbyeAddResumable
   autobahn.wamp.gen.wamp.proto.Goodbye.GoodbyeEnd


.. class:: Goodbye

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsGoodbye(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Reason(self)


   .. method:: Message(self)


   .. method:: Resumable(self)



.. function:: GoodbyeStart(builder)


.. function:: GoodbyeAddReason(builder, reason)


.. function:: GoodbyeAddMessage(builder, message)


.. function:: GoodbyeAddResumable(builder, resumable)


.. function:: GoodbyeEnd(builder)


