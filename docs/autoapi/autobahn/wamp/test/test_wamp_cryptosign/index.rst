:mod:`autobahn.wamp.test.test_wamp_cryptosign`
==============================================

.. py:module:: autobahn.wamp.test.test_wamp_cryptosign


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.test.test_wamp_cryptosign.TestAuth
   autobahn.wamp.test.test_wamp_cryptosign.TestKey



.. data:: keybody
   :annotation: = -----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAa38i/4dNWFuZN/72QAJbyOwZvkUyML/u2b2B1uW4RbQAAAJj4FLyB+BS8
gQAAAAtzc2gtZWQyNTUxOQAAACAa38i/4dNWFuZN/72QAJbyOwZvkUyML/u2b2B1uW4RbQ
AAAEBNV9l6aPVVaWYgpthJwM5YJWhRjXKet1PcfHMt4oBFEBrfyL/h01YW5k3/vZAAlvI7
Bm+RTIwv+7ZvYHW5bhFtAAAAFXNvbWV1c2VyQGZ1bmt0aGF0LmNvbQ==
-----END OPENSSH PRIVATE KEY-----

   

.. data:: pubkey
   :annotation: = ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVp3hjHwIQyEladzd8mFcf0YSXcmyKS3qMLB7VqTQKm someuser@example.com


   

.. data:: testvectors
   

   

.. class:: TestAuth(methodName='runTest')


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


   .. method:: test_valid(self)


   .. method:: test_testvectors(self)


   .. method:: test_authenticator(self)



.. class:: TestKey(methodName='runTest')


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

   .. method:: test_pad(self)


   .. method:: test_key(self)


   .. method:: test_pubkey(self)



