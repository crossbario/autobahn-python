:mod:`autobahn.websocket.test.test_websocket_url`
=================================================

.. py:module:: autobahn.websocket.test.test_websocket_url


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.websocket.test.test_websocket_url.TestCreateWsUrl
   autobahn.websocket.test.test_websocket_url.TestParseWsUrl



.. class:: TestCreateWsUrl(methodName='runTest')


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

   .. method:: test_create_url01(self)


   .. method:: test_create_url02(self)


   .. method:: test_create_url03(self)


   .. method:: test_create_url04(self)


   .. method:: test_create_url05(self)


   .. method:: test_create_url06(self)


   .. method:: test_create_url07(self)


   .. method:: test_create_url08(self)


   .. method:: test_create_url09(self)


   .. method:: test_create_url10(self)


   .. method:: test_create_url11(self)


   .. method:: test_create_url12(self)


   .. method:: test_create_url13(self)


   .. method:: test_create_url14(self)


   .. method:: test_create_url15(self)



.. class:: TestParseWsUrl(methodName='runTest')


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

   .. method:: test_parse_url01(self)


   .. method:: test_parse_url02(self)


   .. method:: test_parse_url03(self)


   .. method:: test_parse_url04(self)


   .. method:: test_parse_url05(self)


   .. method:: test_parse_url06(self)


   .. method:: test_parse_url07(self)


   .. method:: test_parse_url08(self)


   .. method:: test_parse_url09(self)


   .. method:: test_parse_url10(self)


   .. method:: test_parse_url11(self)


   .. method:: test_parse_url12(self)


   .. method:: test_parse_url13(self)


   .. method:: test_parse_url14(self)



