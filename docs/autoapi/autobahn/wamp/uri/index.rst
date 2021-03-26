:mod:`autobahn.wamp.uri`
========================

.. py:module:: autobahn.wamp.uri


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.uri.Pattern



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.uri.convert_starred_uri
   autobahn.wamp.uri.register
   autobahn.wamp.uri.subscribe
   autobahn.wamp.uri.error


.. function:: convert_starred_uri(uri)

   Convert a starred URI to a standard WAMP URI and a detected matching
   policy. A starred URI is one that may contain the character '*' used
   to mark URI wildcard components or URI prefixes. Starred URIs are
   more comfortable / intuitive to use at the user/API level, but need
   to be converted for use on the wire (WAMP protocol level).

   This function takes a possibly starred URI, detects the matching policy
   implied by stars, and returns a pair (uri, match) with any stars
   removed from the URI and the detected matching policy.

   An URI like 'com.example.topic1' (without any stars in it) is
   detected as an exact-matching URI.

   An URI like 'com.example.*' (with exactly one star at the very end)
   is detected as a prefix-matching URI on 'com.example.'.

   An URI like 'com.*.foobar.*' (with more than one star anywhere) is
   detected as a wildcard-matching URI on 'com..foobar.' (in this example,
   there are two wildcard URI components).

   Note that an URI like 'com.example.*' is always detected as
   a prefix-matching URI 'com.example.'. You cannot express a wildcard-matching
   URI 'com.example.' using the starred URI notation! A wildcard matching on
   'com.example.' is different from prefix-matching on 'com.example.' (which
   matches a strict superset of the former!). This is one reason we don't use
   starred URIs for WAMP at the protocol level.


.. class:: Pattern(uri, target, options=None, check_types=False)


   Bases: :class:`object`

   A WAMP URI Pattern.

   .. todo::

      * suffix matches
      * args + kwargs
      * uuid converter
      * multiple URI patterns per decorated object
      * classes: Pattern, EndpointPattern, ..

   .. attribute:: URI_TARGET_ENDPOINT
      :annotation: = 1

      

   .. attribute:: URI_TARGET_HANDLER
      :annotation: = 2

      

   .. attribute:: URI_TARGET_EXCEPTION
      :annotation: = 3

      

   .. attribute:: URI_TYPE_EXACT
      :annotation: = 1

      

   .. attribute:: URI_TYPE_PREFIX
      :annotation: = 2

      

   .. attribute:: URI_TYPE_WILDCARD
      :annotation: = 3

      

   .. attribute:: _URI_COMPONENT
      

      Compiled regular expression for a WAMP URI component.


   .. attribute:: _URI_NAMED_COMPONENT
      

      Compiled regular expression for a named WAMP URI component.

      .. note::
          This pattern is stricter than a general WAMP URI component since a valid Python identifier is required.


   .. attribute:: _URI_NAMED_CONVERTED_COMPONENT
      

      Compiled regular expression for a named and type-converted WAMP URI component.

      .. note::
          This pattern is stricter than a general WAMP URI component since a valid Python identifier is required.


   .. method:: options(self)
      :property:

      Returns the Options instance (if present) for this pattern.

      :return: None or the Options instance
      :rtype: None or RegisterOptions or SubscribeOptions


   .. method:: uri_type(self)
      :property:

      Returns the URI type of this pattern

      :return:
      :rtype: Pattern.URI_TYPE_EXACT, Pattern.URI_TYPE_PREFIX or Pattern.URI_TYPE_WILDCARD


   .. method:: uri(self)

      Returns the original URI (pattern) for this pattern.

      :returns: The URI (pattern), e.g. ``"com.myapp.product.<product:int>.update"``.
      :rtype: str


   .. method:: match(self, uri)

      Match the given (fully qualified) URI according to this pattern
      and return extracted args and kwargs.

      :param uri: The URI to match, e.g. ``"com.myapp.product.123456.update"``.
      :type uri: str

      :returns: A tuple ``(args, kwargs)``
      :rtype: tuple


   .. method:: is_endpoint(self)

      Check if this pattern is for a procedure endpoint.

      :returns: ``True``, iff this pattern is for a procedure endpoint.
      :rtype: bool


   .. method:: is_handler(self)

      Check if this pattern is for an event handler.

      :returns: ``True``, iff this pattern is for an event handler.
      :rtype: bool


   .. method:: is_exception(self)

      Check if this pattern is for an exception.

      :returns: ``True``, iff this pattern is for an exception.
      :rtype: bool



.. function:: register(uri, options=None, check_types=False)

   Decorator for WAMP procedure endpoints.

   :param uri:
   :type uri: str

   :param options:
   :type options: None or RegisterOptions

   :param check_types: Enable automatic type checking against (Python 3.5+) type hints
       specified on the ``endpoint`` callable. Types are checked at run-time on each
       invocation of the ``endpoint`` callable. When a type mismatch occurs, the error
       is forwarded to the callee code in ``onUserError`` override method of
       :class:`autobahn.wamp.protocol.ApplicationSession`. An error
       of type :class:`autobahn.wamp.exception.TypeCheckError` is also raised and
       returned to the caller (via the router).
   :type check_types: bool


.. function:: subscribe(uri, options=None, check_types=False)

   Decorator for WAMP event handlers.

   :param uri:
   :type uri: str

   :param options:
   :type options: None or SubscribeOptions

   :param check_types: Enable automatic type checking against (Python 3.5+) type hints
       specified on the ``endpoint`` callable. Types are checked at run-time on each
       invocation of the ``endpoint`` callable. When a type mismatch occurs, the error
       is forwarded to the callee code in ``onUserError`` override method of
       :class:`autobahn.wamp.protocol.ApplicationSession`. An error
       of type :class:`autobahn.wamp.exception.TypeCheckError` is also raised and
       returned to the caller (via the router).
   :type check_types: bool


.. function:: error(uri)

   Decorator for WAMP error classes.


