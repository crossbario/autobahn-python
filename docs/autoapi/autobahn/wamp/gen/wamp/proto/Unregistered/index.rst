:mod:`autobahn.wamp.gen.wamp.proto.Unregistered`
================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Unregistered


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Unregistered.Unregistered



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Unregistered.UnregisteredStart
   autobahn.wamp.gen.wamp.proto.Unregistered.UnregisteredAddRequest
   autobahn.wamp.gen.wamp.proto.Unregistered.UnregisteredAddRegistration
   autobahn.wamp.gen.wamp.proto.Unregistered.UnregisteredAddReason
   autobahn.wamp.gen.wamp.proto.Unregistered.UnregisteredEnd


.. class:: Unregistered

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsUnregistered(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Registration(self)


   .. method:: Reason(self)



.. function:: UnregisteredStart(builder)


.. function:: UnregisteredAddRequest(builder, request)


.. function:: UnregisteredAddRegistration(builder, registration)


.. function:: UnregisteredAddReason(builder, reason)


.. function:: UnregisteredEnd(builder)


