:mod:`autobahn.wamp.gen.wamp.proto.Principal`
=============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Principal


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Principal.Principal



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Principal.PrincipalStart
   autobahn.wamp.gen.wamp.proto.Principal.PrincipalAddSession
   autobahn.wamp.gen.wamp.proto.Principal.PrincipalAddAuthid
   autobahn.wamp.gen.wamp.proto.Principal.PrincipalAddAuthrole
   autobahn.wamp.gen.wamp.proto.Principal.PrincipalEnd


.. class:: Principal

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsPrincipal(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Session(self)


   .. method:: Authid(self)


   .. method:: Authrole(self)



.. function:: PrincipalStart(builder)


.. function:: PrincipalAddSession(builder, session)


.. function:: PrincipalAddAuthid(builder, authid)


.. function:: PrincipalAddAuthrole(builder, authrole)


.. function:: PrincipalEnd(builder)


