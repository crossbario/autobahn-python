:mod:`autobahn.websocket.test.test_websocket_protocol`
======================================================

.. py:module:: autobahn.websocket.test.test_websocket_protocol


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.websocket.test.test_websocket_protocol.WebSocketClientProtocolTests
   autobahn.websocket.test.test_websocket_protocol.WebSocketServerProtocolTests
   autobahn.websocket.test.test_websocket_protocol.TwistedProtocolTests



.. class:: WebSocketClientProtocolTests(methodName='runTest')


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

   .. method:: setUp(self)

      Hook method for setting up the test fixture before exercising it.


   .. method:: tearDown(self)

      Hook method for deconstructing the test fixture after testing it.


   .. method:: test_auto_ping(self)



.. class:: WebSocketServerProtocolTests(methodName='runTest')


   Bases: :class:`unittest.TestCase`

   Tests for autobahn.websocket.protocol.WebSocketProtocol.

   .. method:: setUp(self)

      Hook method for setting up the test fixture before exercising it.


   .. method:: tearDown(self)

      Hook method for deconstructing the test fixture after testing it.


   .. method:: test_auto_ping(self)


   .. method:: test_sendClose_none(self)

      sendClose with no code or reason works.


   .. method:: test_sendClose_str_reason(self)

      sendClose with a str reason works.


   .. method:: test_sendClose_unicode_reason(self)

      sendClose with a unicode reason works.


   .. method:: test_sendClose_toolong(self)

      sendClose with a too-long reason will truncate it.


   .. method:: test_sendClose_reason_with_no_code(self)

      Trying to sendClose with a reason but no code will raise an Exception.


   .. method:: test_sendClose_invalid_code_type(self)

      Trying to sendClose with a non-int code will raise an Exception.


   .. method:: test_sendClose_invalid_code_value(self)

      Trying to sendClose with a non-valid int code will raise an Exception.



.. class:: TwistedProtocolTests(methodName='runTest')


   Bases: :class:`unittest.TestCase`

   Tests which require a specific framework's protocol class to work
   (in this case, using Twisted)

   .. method:: setUp(self)

      Hook method for setting up the test fixture before exercising it.


   .. method:: tearDown(self)

      Hook method for deconstructing the test fixture after testing it.


   .. method:: test_loseConnection(self)

      If we lose our connection before openHandshakeTimeout fires, it is
      cleaned up



