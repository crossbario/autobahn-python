:mod:`autobahn.nvx.test.test_nvx_utf8validator`
===============================================

.. py:module:: autobahn.nvx.test.test_nvx_utf8validator


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.nvx.test.test_nvx_utf8validator.TestNvxUtf8Validator



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.nvx.test.test_nvx_utf8validator._create_utf8_test_sequences
   autobahn.nvx.test.test_nvx_utf8validator._create_valid_utf8_test_sequences


.. data:: HAS_NVX
   :annotation: = False

   

.. function:: _create_utf8_test_sequences()

   Create test sequences for UTF-8 decoder tests from
   http://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt


.. function:: _create_valid_utf8_test_sequences()

   Generate some exotic, but valid UTF8 test strings.


.. class:: TestNvxUtf8Validator(methodName='runTest')


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


   .. method:: test_standard_utf8validator(self)

      Test standard implementation of UTF8 validator.


   .. method:: test_nvx_utf8validator(self)

      Test NVX implementation of UTF8 validator.


   .. method:: test_standard_utf8validator_incremental(self)

      Test standard implementation of UTF8 validator in incremental mode.


   .. method:: test_nvx_utf8validator_incremental(self)

      Test NVX implementation of UTF8 validator in incremental mode.


   .. method:: _test_utf8(self, validator)


   .. method:: _test_utf8_incremental(self, validator, withPositions=True)



