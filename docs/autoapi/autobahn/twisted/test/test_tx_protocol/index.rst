:mod:`autobahn.twisted.test.test_tx_protocol`
=============================================

.. py:module:: autobahn.twisted.test.test_tx_protocol


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.test.test_tx_protocol.ExceptionHandlingTests
   autobahn.twisted.test.test_tx_protocol.Hixie76RejectionTests
   autobahn.twisted.test.test_tx_protocol.WebSocketOriginMatching
   autobahn.twisted.test.test_tx_protocol.WebSocketXForwardedFor
   autobahn.twisted.test.test_tx_protocol.OnConnectingTests



.. class:: ExceptionHandlingTests(methodName='runTest')


   Bases: :class:`twisted.trial.unittest.TestCase`

   Tests that we format various exception variations properly during
   connectionLost

   .. method:: setUp(self)

      Hook method for setting up the test fixture before exercising it.


   .. method:: tearDown(self)

      Hook method for deconstructing the test fixture after testing it.


   .. method:: test_connection_done(self)


   .. method:: test_connection_aborted(self)


   .. method:: test_connection_lost(self)


   .. method:: test_connection_lost_arg(self)



.. class:: Hixie76RejectionTests(methodName='runTest')


   Bases: :class:`twisted.trial.unittest.TestCase`

   Hixie-76 should not be accepted by an Autobahn server.

   .. method:: test_handshake_fails(self)

      A handshake from a client only supporting Hixie-76 will fail.



.. class:: WebSocketOriginMatching(methodName='runTest')


   Bases: :class:`twisted.trial.unittest.TestCase`

   Test that we match Origin: headers properly, when asked to

   .. method:: setUp(self)

      Hook method for setting up the test fixture before exercising it.


   .. method:: tearDown(self)

      Hook method for deconstructing the test fixture after testing it.


   .. method:: test_match_full_origin(self)


   .. method:: test_match_wrong_scheme_origin(self)


   .. method:: test_match_origin_secure_scheme(self)


   .. method:: test_match_origin_documentation_example(self)

      Test the examples from the docs


   .. method:: test_match_origin_examples(self)

      All the example origins from RFC6454 (3.2.1)


   .. method:: test_match_origin_counter_examples(self)

      All the example 'not-same' origins from RFC6454 (3.2.1)


   .. method:: test_match_origin_edge(self)


   .. method:: test_origin_from_url(self)


   .. method:: test_origin_file(self)


   .. method:: test_origin_null(self)



.. class:: WebSocketXForwardedFor(methodName='runTest')


   Bases: :class:`twisted.trial.unittest.TestCase`

   Test that (only) a trusted X-Forwarded-For can replace the peer address.

   .. method:: setUp(self)

      Hook method for setting up the test fixture before exercising it.


   .. method:: tearDown(self)

      Hook method for deconstructing the test fixture after testing it.


   .. method:: test_trusted_addresses(self)



.. class:: OnConnectingTests(methodName='runTest')


   Bases: :class:`twisted.trial.unittest.TestCase`

   Tests related to onConnecting callback

   These tests are testing generic behavior, but are somewhat tied to
   'a framework' so we're just testing using Twisted-specifics here.

   .. method:: test_on_connecting_client_fails(self)


   .. method:: test_on_connecting_client_success(self)


   .. method:: test_str_transport(self)


   .. method:: test_str_connecting(self)



