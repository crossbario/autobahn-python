:mod:`autobahn.wamp.gen.wamp.proto.AuthCryptosignChallenge`
===========================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.AuthCryptosignChallenge


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthCryptosignChallenge.AuthCryptosignChallenge



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthCryptosignChallenge.AuthCryptosignChallengeStart
   autobahn.wamp.gen.wamp.proto.AuthCryptosignChallenge.AuthCryptosignChallengeAddChannelBinding
   autobahn.wamp.gen.wamp.proto.AuthCryptosignChallenge.AuthCryptosignChallengeEnd


.. class:: AuthCryptosignChallenge

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsAuthCryptosignChallenge(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: ChannelBinding(self)



.. function:: AuthCryptosignChallengeStart(builder)


.. function:: AuthCryptosignChallengeAddChannelBinding(builder, channelBinding)


.. function:: AuthCryptosignChallengeEnd(builder)


