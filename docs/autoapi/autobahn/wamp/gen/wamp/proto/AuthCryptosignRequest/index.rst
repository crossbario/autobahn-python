:mod:`autobahn.wamp.gen.wamp.proto.AuthCryptosignRequest`
=========================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.AuthCryptosignRequest


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthCryptosignRequest.AuthCryptosignRequest



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthCryptosignRequest.AuthCryptosignRequestStart
   autobahn.wamp.gen.wamp.proto.AuthCryptosignRequest.AuthCryptosignRequestAddPubkey
   autobahn.wamp.gen.wamp.proto.AuthCryptosignRequest.AuthCryptosignRequestAddChannelBinding
   autobahn.wamp.gen.wamp.proto.AuthCryptosignRequest.AuthCryptosignRequestEnd


.. class:: AuthCryptosignRequest

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsAuthCryptosignRequest(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Pubkey(self)


   .. method:: ChannelBinding(self)



.. function:: AuthCryptosignRequestStart(builder)


.. function:: AuthCryptosignRequestAddPubkey(builder, pubkey)


.. function:: AuthCryptosignRequestAddChannelBinding(builder, channelBinding)


.. function:: AuthCryptosignRequestEnd(builder)


