:mod:`autobahn.wamp.test.test_wamp_auth`
========================================

.. py:module:: autobahn.wamp.test.test_wamp_auth


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.test.test_wamp_auth.TestWampAuthHelpers
   autobahn.wamp.test.test_wamp_auth.TestScram



.. data:: PBKDF2_TEST_VECTORS
   :annotation: = [[b'password', b'salt', 1, 20, '0c60c80f961f0e71f3a9b524af6012062fe037a6'], [b'password', b'salt', 2, 20, 'ea6c014dc72d6f8ccd1ed92ace1d41f0d8de8957'], [b'password', b'ATHENA.MIT.EDUraeburn', 1, 16, 'cdedb5281bb2f801565a1122b2563515'], [b'password', b'ATHENA.MIT.EDUraeburn', 1, 32, 'cdedb5281bb2f801565a1122b25635150ad1f7a04bb9f3a333ecc0e2e1f70837'], [b'password', b'ATHENA.MIT.EDUraeburn', 2, 16, '01dbee7f4a9e243e988b62c73cda935d'], [b'password', b'ATHENA.MIT.EDUraeburn', 2, 32, '01dbee7f4a9e243e988b62c73cda935da05378b93244ec8f48a99e61ad799d86'], [b'password', b'ATHENA.MIT.EDUraeburn', 1200, 32, '5c08eb61fdf71e4e4ec3cf6ba1f5512ba7e52ddbc5e5142f708a31e2e62b1e13'], None, None]

   

.. class:: TestWampAuthHelpers(methodName='runTest')


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

   .. method:: test_pbkdf2(self)


   .. method:: test_generate_totp_secret_default(self)


   .. method:: test_generate_totp_secret_length(self)


   .. method:: test_compute_totp(self)


   .. method:: test_compute_totp_offset(self)


   .. method:: test_derive_key(self)


   .. method:: test_generate_wcs_default(self)


   .. method:: test_generate_wcs_length(self)


   .. method:: test_compute_wcs(self)



.. class:: TestScram(methodName='runTest')


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

   .. method:: test_argon2id_static(self)


   .. method:: test_pbkdf2_static(self)


   .. method:: test_basic(self)


   .. method:: test_no_memory_arg(self)


   .. method:: test_unknown_arg(self)



