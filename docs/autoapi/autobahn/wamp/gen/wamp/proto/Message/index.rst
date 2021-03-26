:mod:`autobahn.wamp.gen.wamp.proto.Message`
===========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Message


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Message.Message



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Message.MessageStart
   autobahn.wamp.gen.wamp.proto.Message.MessageAddMsgType
   autobahn.wamp.gen.wamp.proto.Message.MessageAddMsg
   autobahn.wamp.gen.wamp.proto.Message.MessageEnd


.. class:: Message

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsMessage(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: MsgType(self)


   .. method:: Msg(self)



.. function:: MessageStart(builder)


.. function:: MessageAddMsgType(builder, msgType)


.. function:: MessageAddMsg(builder, msg)


.. function:: MessageEnd(builder)


