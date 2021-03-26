:mod:`autobahn.wamp.gen.wamp.proto.Published`
=============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Published


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Published.Published



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Published.PublishedStart
   autobahn.wamp.gen.wamp.proto.Published.PublishedAddRequest
   autobahn.wamp.gen.wamp.proto.Published.PublishedAddPublication
   autobahn.wamp.gen.wamp.proto.Published.PublishedEnd


.. class:: Published

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsPublished(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Publication(self)



.. function:: PublishedStart(builder)


.. function:: PublishedAddRequest(builder, request)


.. function:: PublishedAddPublication(builder, publication)


.. function:: PublishedEnd(builder)


