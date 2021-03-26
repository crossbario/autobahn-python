:mod:`autobahn.wamp.gen.wamp.proto.Cancel`
==========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Cancel


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Cancel.Cancel



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Cancel.CancelStart
   autobahn.wamp.gen.wamp.proto.Cancel.CancelAddRequest
   autobahn.wamp.gen.wamp.proto.Cancel.CancelAddMode
   autobahn.wamp.gen.wamp.proto.Cancel.CancelEnd


.. class:: Cancel

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsCancel(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Mode(self)



.. function:: CancelStart(builder)


.. function:: CancelAddRequest(builder, request)


.. function:: CancelAddMode(builder, mode)


.. function:: CancelEnd(builder)


