:mod:`autobahn.wamp.gen.wamp.proto.Welcome`
===========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Welcome


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Welcome.Welcome



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeStart
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddRoles
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddSession
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddRealm
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddAuthid
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddAuthrole
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddAuthmethod
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddAuthprovider
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddAuthextra
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddResumed
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddResumable
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeAddResumeToken
   autobahn.wamp.gen.wamp.proto.Welcome.WelcomeEnd


.. class:: Welcome

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsWelcome(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Roles(self)


   .. method:: Session(self)


   .. method:: Realm(self)


   .. method:: Authid(self)


   .. method:: Authrole(self)


   .. method:: Authmethod(self)


   .. method:: Authprovider(self)


   .. method:: Authextra(self)


   .. method:: Resumed(self)


   .. method:: Resumable(self)


   .. method:: ResumeToken(self)



.. function:: WelcomeStart(builder)


.. function:: WelcomeAddRoles(builder, roles)


.. function:: WelcomeAddSession(builder, session)


.. function:: WelcomeAddRealm(builder, realm)


.. function:: WelcomeAddAuthid(builder, authid)


.. function:: WelcomeAddAuthrole(builder, authrole)


.. function:: WelcomeAddAuthmethod(builder, authmethod)


.. function:: WelcomeAddAuthprovider(builder, authprovider)


.. function:: WelcomeAddAuthextra(builder, authextra)


.. function:: WelcomeAddResumed(builder, resumed)


.. function:: WelcomeAddResumable(builder, resumable)


.. function:: WelcomeAddResumeToken(builder, resumeToken)


.. function:: WelcomeEnd(builder)


