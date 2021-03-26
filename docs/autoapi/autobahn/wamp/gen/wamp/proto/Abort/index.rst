:mod:`autobahn.wamp.gen.wamp.proto.Abort`
=========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Abort


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Abort.Abort



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Abort.AbortStart
   autobahn.wamp.gen.wamp.proto.Abort.AbortAddReason
   autobahn.wamp.gen.wamp.proto.Abort.AbortAddMessage
   autobahn.wamp.gen.wamp.proto.Abort.AbortEnd


.. class:: Abort

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsAbort(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Reason(self)


   .. method:: Message(self)



.. function:: AbortStart(builder)


.. function:: AbortAddReason(builder, reason)


.. function:: AbortAddMessage(builder, message)


.. function:: AbortEnd(builder)


