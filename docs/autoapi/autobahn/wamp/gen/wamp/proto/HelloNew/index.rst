:mod:`autobahn.wamp.gen.wamp.proto.HelloNew`
============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.HelloNew


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNew



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewStart
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddRoles
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddRealm
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddAuthid
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddAuthrole
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddAuthmode
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddAuthfactor1Type
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddAuthfactor1
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddAuthfactor2Type
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddAuthfactor2
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddAuthfactor3Type
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddAuthfactor3
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddResumable
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddResumeSession
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewAddResumeToken
   autobahn.wamp.gen.wamp.proto.HelloNew.HelloNewEnd


.. class:: HelloNew

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsHelloNew(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Roles(self)


   .. method:: Realm(self)


   .. method:: Authid(self)


   .. method:: Authrole(self)


   .. method:: Authmode(self)


   .. method:: Authfactor1Type(self)


   .. method:: Authfactor1(self)


   .. method:: Authfactor2Type(self)


   .. method:: Authfactor2(self)


   .. method:: Authfactor3Type(self)


   .. method:: Authfactor3(self)


   .. method:: Resumable(self)


   .. method:: ResumeSession(self)


   .. method:: ResumeToken(self)



.. function:: HelloNewStart(builder)


.. function:: HelloNewAddRoles(builder, roles)


.. function:: HelloNewAddRealm(builder, realm)


.. function:: HelloNewAddAuthid(builder, authid)


.. function:: HelloNewAddAuthrole(builder, authrole)


.. function:: HelloNewAddAuthmode(builder, authmode)


.. function:: HelloNewAddAuthfactor1Type(builder, authfactor1Type)


.. function:: HelloNewAddAuthfactor1(builder, authfactor1)


.. function:: HelloNewAddAuthfactor2Type(builder, authfactor2Type)


.. function:: HelloNewAddAuthfactor2(builder, authfactor2)


.. function:: HelloNewAddAuthfactor3Type(builder, authfactor3Type)


.. function:: HelloNewAddAuthfactor3(builder, authfactor3)


.. function:: HelloNewAddResumable(builder, resumable)


.. function:: HelloNewAddResumeSession(builder, resumeSession)


.. function:: HelloNewAddResumeToken(builder, resumeToken)


.. function:: HelloNewEnd(builder)


