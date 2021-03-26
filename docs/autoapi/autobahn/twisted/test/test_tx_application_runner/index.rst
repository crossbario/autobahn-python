:mod:`autobahn.twisted.test.test_tx_application_runner`
=======================================================

.. py:module:: autobahn.twisted.test.test_tx_application_runner


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.test.test_tx_application_runner.TestApplicationRunner



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.twisted.test.test_tx_application_runner.raise_error


.. function:: raise_error(*args, **kw)


.. class:: TestApplicationRunner(methodName='runTest')


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

   .. method:: test_runner_default(self, fakereactor)


   .. method:: test_runner_no_run(self, fakereactor)


   .. method:: test_runner_no_run_happypath(self, fakereactor)


   .. method:: test_runner_bad_proxy(self, fakereactor)


   .. method:: test_runner_proxy(self, fakereactor)



