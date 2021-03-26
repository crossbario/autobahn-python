:mod:`autobahn.wamp.gen.wamp.Map`
=================================

.. py:module:: autobahn.wamp.gen.wamp.Map


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.Map.Map



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.Map.MapStart
   autobahn.wamp.gen.wamp.Map.MapAddKey
   autobahn.wamp.gen.wamp.Map.MapAddValue
   autobahn.wamp.gen.wamp.Map.MapEnd


.. class:: Map

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsMap(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Key(self)


   .. method:: Value(self)



.. function:: MapStart(builder)


.. function:: MapAddKey(builder, key)


.. function:: MapAddValue(builder, value)


.. function:: MapEnd(builder)


