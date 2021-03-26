:mod:`autobahn.testutil`
========================

.. py:module:: autobahn.testutil


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.testutil.FakeTransport



.. class:: FakeTransport


   Bases: :class:`object`

   .. attribute:: _written
      :annotation: = b''

      

   .. attribute:: _open
      :annotation: = True

      

   .. method:: abortConnection(self, *args, **kw)


   .. method:: write(self, msg)


   .. method:: loseConnection(self)


   .. method:: registerProducer(self, producer, streaming)
      :abstractmethod:


   .. method:: unregisterProducer(self)


   .. method:: getPeer(self)


   .. method:: getHost(self)


   .. method:: abort_called(self)



