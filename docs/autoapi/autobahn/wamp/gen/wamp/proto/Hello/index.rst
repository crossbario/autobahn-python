:mod:`autobahn.wamp.gen.wamp.proto.Hello`
=========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Hello


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Hello.Hello



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Hello.HelloStart
   autobahn.wamp.gen.wamp.proto.Hello.HelloAddRoles
   autobahn.wamp.gen.wamp.proto.Hello.HelloAddRealm
   autobahn.wamp.gen.wamp.proto.Hello.HelloAddAuthmethods
   autobahn.wamp.gen.wamp.proto.Hello.HelloStartAuthmethodsVector
   autobahn.wamp.gen.wamp.proto.Hello.HelloAddAuthid
   autobahn.wamp.gen.wamp.proto.Hello.HelloAddAuthrole
   autobahn.wamp.gen.wamp.proto.Hello.HelloAddAuthextra
   autobahn.wamp.gen.wamp.proto.Hello.HelloAddResumable
   autobahn.wamp.gen.wamp.proto.Hello.HelloAddResumeSession
   autobahn.wamp.gen.wamp.proto.Hello.HelloAddResumeToken
   autobahn.wamp.gen.wamp.proto.Hello.HelloEnd


.. class:: Hello

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsHello(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Roles(self)


   .. method:: Realm(self)


   .. method:: Authmethods(self, j)


   .. method:: AuthmethodsAsNumpy(self)


   .. method:: AuthmethodsLength(self)


   .. method:: Authid(self)


   .. method:: Authrole(self)


   .. method:: Authextra(self)


   .. method:: Resumable(self)


   .. method:: ResumeSession(self)


   .. method:: ResumeToken(self)



.. function:: HelloStart(builder)


.. function:: HelloAddRoles(builder, roles)


.. function:: HelloAddRealm(builder, realm)


.. function:: HelloAddAuthmethods(builder, authmethods)


.. function:: HelloStartAuthmethodsVector(builder, numElems)


.. function:: HelloAddAuthid(builder, authid)


.. function:: HelloAddAuthrole(builder, authrole)


.. function:: HelloAddAuthextra(builder, authextra)


.. function:: HelloAddResumable(builder, resumable)


.. function:: HelloAddResumeSession(builder, resumeSession)


.. function:: HelloAddResumeToken(builder, resumeToken)


.. function:: HelloEnd(builder)


