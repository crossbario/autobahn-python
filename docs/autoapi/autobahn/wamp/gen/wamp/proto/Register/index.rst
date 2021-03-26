:mod:`autobahn.wamp.gen.wamp.proto.Register`
============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Register


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Register.Register



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Register.RegisterStart
   autobahn.wamp.gen.wamp.proto.Register.RegisterAddRequest
   autobahn.wamp.gen.wamp.proto.Register.RegisterAddProcedure
   autobahn.wamp.gen.wamp.proto.Register.RegisterAddMatch
   autobahn.wamp.gen.wamp.proto.Register.RegisterAddInvoke
   autobahn.wamp.gen.wamp.proto.Register.RegisterAddConcurrency
   autobahn.wamp.gen.wamp.proto.Register.RegisterAddForceReregister
   autobahn.wamp.gen.wamp.proto.Register.RegisterEnd


.. class:: Register

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsRegister(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Procedure(self)


   .. method:: Match(self)


   .. method:: Invoke(self)


   .. method:: Concurrency(self)


   .. method:: ForceReregister(self)



.. function:: RegisterStart(builder)


.. function:: RegisterAddRequest(builder, request)


.. function:: RegisterAddProcedure(builder, procedure)


.. function:: RegisterAddMatch(builder, match)


.. function:: RegisterAddInvoke(builder, invoke)


.. function:: RegisterAddConcurrency(builder, concurrency)


.. function:: RegisterAddForceReregister(builder, forceReregister)


.. function:: RegisterEnd(builder)


