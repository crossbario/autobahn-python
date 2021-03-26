:mod:`autobahn.wamp.test.test_wamp_runner`
==========================================

.. py:module:: autobahn.wamp.test.test_wamp_runner


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.test.test_wamp_runner.FakeReactor



.. class:: FakeReactor(to_raise)


   Bases: :class:`object`

   This just fakes out enough reactor methods so .run() can work.

   .. attribute:: stop_called
      :annotation: = False

      

   .. method:: run(self, *args, **kw)


   .. method:: stop(self)


   .. method:: callLater(self, delay, func, *args, **kwargs)


   .. method:: connectTCP(self, *args, **kw)



