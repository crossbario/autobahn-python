:mod:`autobahn.wamp.gen.wamp.proto.AuthScramWelcome`
====================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.AuthScramWelcome


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthScramWelcome.AuthScramWelcome



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.AuthScramWelcome.AuthScramWelcomeStart
   autobahn.wamp.gen.wamp.proto.AuthScramWelcome.AuthScramWelcomeAddVerifier
   autobahn.wamp.gen.wamp.proto.AuthScramWelcome.AuthScramWelcomeEnd


.. class:: AuthScramWelcome

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsAuthScramWelcome(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Verifier(self)



.. function:: AuthScramWelcomeStart(builder)


.. function:: AuthScramWelcomeAddVerifier(builder, verifier)


.. function:: AuthScramWelcomeEnd(builder)


