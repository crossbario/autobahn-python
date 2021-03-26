:mod:`autobahn.wamp.test.test_wamp_serializer`
==============================================

.. py:module:: autobahn.wamp.test.test_wamp_serializer


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.test.test_wamp_serializer.TestFlatBuffersSerializer
   autobahn.wamp.test.test_wamp_serializer.TestSerializer



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.test.test_wamp_serializer.generate_test_messages
   autobahn.wamp.test.test_wamp_serializer.generate_test_messages_binary
   autobahn.wamp.test.test_wamp_serializer.create_serializers


.. function:: generate_test_messages()

   List of WAMP test message used for serializers. Expand this if you add more
   options or messages.

   This list of WAMP message does not contain any binary app payloads!


.. function:: generate_test_messages_binary()

   Generate WAMP test messages which contain binary app payloads.

   With the JSON serializer, this currently only works on Python 3 (both CPython3 and PyPy3),
   because even on Python 3, we need to patch the stdlib JSON, and on Python 2, the patching
   would be even hackier.


.. function:: create_serializers()


.. class:: TestFlatBuffersSerializer(methodName='runTest')


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

   .. method:: test_basic(self)



.. class:: TestSerializer(methodName='runTest')


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


   .. method:: test_deep_equal_msg(self)

      Test deep object equality assert (because I am paranoid).


   .. method:: test_roundtrip_msg(self)

      Test round-tripping over each serializer.


   .. method:: test_crosstrip_msg(self)

      Test cross-tripping over 2 serializers (as is done by WAMP routers).


   .. method:: test_cache_msg(self)

      Test message serialization caching.


   .. method:: test_initial_stats(self)

      Test initial serializer stats are indeed empty.


   .. method:: test_serialize_stats(self)

      Test serializer stats are non-empty after serializing/unserializing messages.


   .. method:: test_serialize_stats_with_details(self)

      Test serializer stats - with details - are non-empty after serializing/unserializing messages.


   .. method:: test_reset_stats(self)

      Test serializer stats are reset after fetching stats - depending on option.


   .. method:: test_auto_stats(self)

      Test serializer stats are non-empty after serializing/unserializing messages.



