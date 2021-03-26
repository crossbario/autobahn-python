:mod:`autobahn.wamp.message_fbs`
================================

.. py:module:: autobahn.wamp.message_fbs


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.message_fbs.MessageType
   autobahn.wamp.message_fbs.Event




.. class:: Event

   Bases: :class:`autobahn.wamp.gen.wamp.proto.Event.Event`

   .. method:: GetRootAsEvent(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: ArgsAsBytes(self)


   .. method:: KwargsAsBytes(self)


   .. method:: PayloadAsBytes(self)


   .. method:: EncKeyAsBytes(self)



