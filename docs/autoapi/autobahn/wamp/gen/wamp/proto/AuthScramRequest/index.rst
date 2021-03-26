:mod:`autobahn.wamp.gen.wamp.proto.AuthScramRequest`
====================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.AuthScramRequest


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthScramRequest.AuthScramRequest



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthScramRequest.AuthScramRequestStart
   autobahn.wamp.gen.wamp.proto.AuthScramRequest.AuthScramRequestAddNonce
   autobahn.wamp.gen.wamp.proto.AuthScramRequest.AuthScramRequestAddChannelBinding
   autobahn.wamp.gen.wamp.proto.AuthScramRequest.AuthScramRequestEnd


.. class:: AuthScramRequest

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsAuthScramRequest(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Nonce(self)


   .. method:: ChannelBinding(self)



.. function:: AuthScramRequestStart(builder)


.. function:: AuthScramRequestAddNonce(builder, nonce)


.. function:: AuthScramRequestAddChannelBinding(builder, channelBinding)


.. function:: AuthScramRequestEnd(builder)


