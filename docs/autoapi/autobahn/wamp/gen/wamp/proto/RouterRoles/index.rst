:mod:`autobahn.wamp.gen.wamp.proto.RouterRoles`
===============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.RouterRoles


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.RouterRoles.RouterRoles



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.RouterRoles.RouterRolesStart
   autobahn.wamp.gen.wamp.proto.RouterRoles.RouterRolesAddBroker
   autobahn.wamp.gen.wamp.proto.RouterRoles.RouterRolesAddDealer
   autobahn.wamp.gen.wamp.proto.RouterRoles.RouterRolesEnd


.. class:: RouterRoles

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsRouterRoles(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Broker(self)


   .. method:: Dealer(self)



.. function:: RouterRolesStart(builder)


.. function:: RouterRolesAddBroker(builder, broker)


.. function:: RouterRolesAddDealer(builder, dealer)


.. function:: RouterRolesEnd(builder)


