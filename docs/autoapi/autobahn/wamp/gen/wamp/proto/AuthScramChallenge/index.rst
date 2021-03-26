:mod:`autobahn.wamp.gen.wamp.proto.AuthScramChallenge`
======================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.AuthScramChallenge


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallenge



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallengeStart
   autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallengeAddNonce
   autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallengeAddSalt
   autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallengeAddKdf
   autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallengeAddIterations
   autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallengeAddMemory
   autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallengeAddChannelBinding
   autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallengeEnd


.. class:: AuthScramChallenge

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsAuthScramChallenge(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Nonce(self)


   .. method:: Salt(self)


   .. method:: Kdf(self)


   .. method:: Iterations(self)


   .. method:: Memory(self)


   .. method:: ChannelBinding(self)



.. function:: AuthScramChallengeStart(builder)


.. function:: AuthScramChallengeAddNonce(builder, nonce)


.. function:: AuthScramChallengeAddSalt(builder, salt)


.. function:: AuthScramChallengeAddKdf(builder, kdf)


.. function:: AuthScramChallengeAddIterations(builder, iterations)


.. function:: AuthScramChallengeAddMemory(builder, memory)


.. function:: AuthScramChallengeAddChannelBinding(builder, channelBinding)


.. function:: AuthScramChallengeEnd(builder)


