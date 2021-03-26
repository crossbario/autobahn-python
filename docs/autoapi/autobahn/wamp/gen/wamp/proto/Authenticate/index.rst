:mod:`autobahn.wamp.gen.wamp.proto.Authenticate`
================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Authenticate


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Authenticate.Authenticate



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Authenticate.AuthenticateStart
   autobahn.wamp.gen.wamp.proto.Authenticate.AuthenticateAddSignature
   autobahn.wamp.gen.wamp.proto.Authenticate.AuthenticateAddExtra
   autobahn.wamp.gen.wamp.proto.Authenticate.AuthenticateEnd


.. class:: Authenticate

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsAuthenticate(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Signature(self)


   .. method:: Extra(self)



.. function:: AuthenticateStart(builder)


.. function:: AuthenticateAddSignature(builder, signature)


.. function:: AuthenticateAddExtra(builder, extra)


.. function:: AuthenticateEnd(builder)


