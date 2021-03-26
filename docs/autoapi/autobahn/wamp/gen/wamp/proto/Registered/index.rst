:mod:`autobahn.wamp.gen.wamp.proto.Registered`
==============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Registered


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Registered.Registered



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Registered.RegisteredStart
   autobahn.wamp.gen.wamp.proto.Registered.RegisteredAddRequest
   autobahn.wamp.gen.wamp.proto.Registered.RegisteredAddRegistration
   autobahn.wamp.gen.wamp.proto.Registered.RegisteredEnd


.. class:: Registered

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsRegistered(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Registration(self)



.. function:: RegisteredStart(builder)


.. function:: RegisteredAddRequest(builder, request)


.. function:: RegisteredAddRegistration(builder, registration)


.. function:: RegisteredEnd(builder)


