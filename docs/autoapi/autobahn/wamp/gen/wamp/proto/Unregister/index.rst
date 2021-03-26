:mod:`autobahn.wamp.gen.wamp.proto.Unregister`
==============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Unregister


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Unregister.Unregister



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Unregister.UnregisterStart
   autobahn.wamp.gen.wamp.proto.Unregister.UnregisterAddRequest
   autobahn.wamp.gen.wamp.proto.Unregister.UnregisterAddRegistration
   autobahn.wamp.gen.wamp.proto.Unregister.UnregisterEnd


.. class:: Unregister

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsUnregister(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Registration(self)



.. function:: UnregisterStart(builder)


.. function:: UnregisterAddRequest(builder, request)


.. function:: UnregisterAddRegistration(builder, registration)


.. function:: UnregisterEnd(builder)


