:mod:`autobahn.wamp.test.test_wamp_websocket`
=============================================

.. py:module:: autobahn.wamp.test.test_wamp_websocket


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.test.test_wamp_websocket.TestWebsocketProtocol



.. class:: TestWebsocketProtocol(methodName='runTest')


   Bases: :class:`twisted.trial.unittest.TestCase`

   A unit test. The atom of the unit testing universe.

   This class extends L{SynchronousTestCase} which extends C{unittest.TestCase}
   from the standard library. The main feature is the ability to return
   C{Deferred}s from tests and fixture methods and to have the suite wait for
   those C{Deferred}s to fire.  Also provides new assertions such as
   L{assertFailure}.

   @ivar timeout: A real number of seconds. If set, the test will
   raise an error if it takes longer than C{timeout} seconds.
   If not set, util.DEFAULT_TIMEOUT_DURATION is used.

   .. method:: setUp(self)

      Hook method for setting up the test fixture before exercising it.


   .. method:: test_close_before_open(self)



