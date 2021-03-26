:mod:`autobahn.wamp.gen.wamp.proto.AuthCraChallenge`
====================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.AuthCraChallenge


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthCraChallenge.AuthCraChallenge



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthCraChallenge.AuthCraChallengeStart
   autobahn.wamp.gen.wamp.proto.AuthCraChallenge.AuthCraChallengeAddChallenge
   autobahn.wamp.gen.wamp.proto.AuthCraChallenge.AuthCraChallengeAddSalt
   autobahn.wamp.gen.wamp.proto.AuthCraChallenge.AuthCraChallengeAddIterations
   autobahn.wamp.gen.wamp.proto.AuthCraChallenge.AuthCraChallengeAddKeylen
   autobahn.wamp.gen.wamp.proto.AuthCraChallenge.AuthCraChallengeEnd


.. class:: AuthCraChallenge

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsAuthCraChallenge(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Challenge(self)


   .. method:: Salt(self)


   .. method:: Iterations(self)


   .. method:: Keylen(self)



.. function:: AuthCraChallengeStart(builder)


.. function:: AuthCraChallengeAddChallenge(builder, challenge)


.. function:: AuthCraChallengeAddSalt(builder, salt)


.. function:: AuthCraChallengeAddIterations(builder, iterations)


.. function:: AuthCraChallengeAddKeylen(builder, keylen)


.. function:: AuthCraChallengeEnd(builder)


