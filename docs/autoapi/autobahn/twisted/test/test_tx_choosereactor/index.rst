:mod:`autobahn.twisted.test.test_tx_choosereactor`
==================================================

.. py:module:: autobahn.twisted.test.test_tx_choosereactor


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.test.test_tx_choosereactor.ChooseReactorTests



.. class:: ChooseReactorTests(methodName='runTest')


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

   .. method:: patch_reactor(self, name, new_reactor)

      Patch ``name`` so that Twisted will grab a fake reactor instead of
      a real one.


   .. method:: patch_modules(self)

      Patch ``sys.modules`` so that Twisted believes there is no
      installed reactor.


   .. method:: test_unknown(self)

      ``install_optimal_reactor`` will use the default reactor if it is
      unable to detect the platform it is running on.


   .. method:: test_mac(self)

      ``install_optimal_reactor`` will install KQueueReactor on
      Darwin (OS X).


   .. method:: test_win(self)

      ``install_optimal_reactor`` will install IOCPReactor on Windows.


   .. method:: test_bsd(self)

      ``install_optimal_reactor`` will install KQueueReactor on BSD.


   .. method:: test_linux(self)

      ``install_optimal_reactor`` will install EPollReactor on Linux.



