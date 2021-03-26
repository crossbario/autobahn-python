:mod:`autobahn.twisted.test.test_tx_component`
==============================================

.. py:module:: autobahn.twisted.test.test_tx_component


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.test.test_tx_component.ConnectionTests



.. class:: ConnectionTests(methodName='runTest')


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


   .. method:: test_successful_connect(self, fake_sleep)


   .. method:: test_successful_proxy_connect(self, fake_sleep)


   .. method:: test_cancel(self, fake_sleep)

      if we start a component but call .stop before it connects, ever,
      it should still exit properly


   .. method:: test_cancel_while_waiting(self)

      if we start a component but call .stop before it connects, ever,
      it should still exit properly -- even if we're 'between'
      connection attempts


   .. method:: test_connect_no_auth_method(self, fake_sleep)



