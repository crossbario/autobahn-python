:mod:`autobahn.asyncio.test.test_aio_rawsocket`
===============================================

.. py:module:: autobahn.asyncio.test.test_aio_rawsocket


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.asyncio.test.test_aio_rawsocket.Test



.. class:: Test(methodName='runTest')


   Bases: :class:`unittest.TestCase`

   A class whose instances are single test cases.

   By default, the test code itself should be placed in a method named
   'runTest'.

   If the fixture may be used for many test cases, create as
   many test methods as are needed. When instantiating such a TestCase
   subclass, specify in the constructor arguments the name of the test method
   that the instance is to execute.

   Test authors should subclass TestCase for their own tests. Construction
   and deconstruction of the test's environment ('fixture') can be
   implemented by overriding the 'setUp' and 'tearDown' methods respectively.

   If it is necessary to override the __init__ method, the base class
   __init__ method must always be called. It is important that subclasses
   should not change the signature of their __init__ method, since instances
   of the classes are instantiated automatically by parts of the framework
   in order to be run.

   When subclassing TestCase, you can set these attributes:
   * failureException: determines which exception will be raised when
       the instance's assertion methods fail; test methods raising this
       exception will be deemed to have 'failed' rather than 'errored'.
   * longMessage: determines whether long messages (including repr of
       objects used in assert methods) will be printed on failure in *addition*
       to any explicit message passed.
   * maxDiff: sets the maximum length of a diff in failure messages
       by assert methods using difflib. It is looked up as an instance
       attribute so can be configured by individual tests if required.

   .. method:: test_sers(self)


   .. method:: test_prefix(self)


   .. method:: test_is_closed(self)


   .. method:: test_raw_socket_server1(self)


   .. method:: test_raw_socket_server_errors(self)


   .. method:: test_raw_socket_client1(self)


   .. method:: test_raw_socket_client_error(self)


   .. method:: test_wamp(self)



