:mod:`autobahn.wamp.gen.wamp.proto.ClientRoles`
===============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.ClientRoles


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.ClientRoles.ClientRoles



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.ClientRoles.ClientRolesStart
   autobahn.wamp.gen.wamp.proto.ClientRoles.ClientRolesAddPublisher
   autobahn.wamp.gen.wamp.proto.ClientRoles.ClientRolesAddSubscriber
   autobahn.wamp.gen.wamp.proto.ClientRoles.ClientRolesAddCaller
   autobahn.wamp.gen.wamp.proto.ClientRoles.ClientRolesAddCallee
   autobahn.wamp.gen.wamp.proto.ClientRoles.ClientRolesEnd


.. class:: ClientRoles

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsClientRoles(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Publisher(self)


   .. method:: Subscriber(self)


   .. method:: Caller(self)


   .. method:: Callee(self)



.. function:: ClientRolesStart(builder)


.. function:: ClientRolesAddPublisher(builder, publisher)


.. function:: ClientRolesAddSubscriber(builder, subscriber)


.. function:: ClientRolesAddCaller(builder, caller)


.. function:: ClientRolesAddCallee(builder, callee)


.. function:: ClientRolesEnd(builder)


