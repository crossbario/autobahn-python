:mod:`autobahn.util`
====================

.. py:module:: autobahn.util


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.util.IdGenerator
   autobahn.util.Stopwatch
   autobahn.util.Tracker
   autobahn.util.EqualityMixin
   autobahn.util.ObservableMixin



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.util.public
   autobahn.util.encode_truncate
   autobahn.util.xor
   autobahn.util.utcstr
   autobahn.util.utcnow
   autobahn.util.rid
   autobahn.util.id
   autobahn.util.newid
   autobahn.util.generate_token
   autobahn.util.generate_activation_code
   autobahn.util.generate_user_password
   autobahn.util.generate_serial_number
   autobahn.util.rtime


.. function:: public(obj)

   The public user API of Autobahn is marked using this decorator.
   Everything that is not decorated @public is library internal, can
   change at any time and should not be used in user program code.


.. function:: encode_truncate(text, limit, encoding='utf8', return_encoded=True)

   Given a string, return a truncated version of the string such that
   the UTF8 encoding of the string is smaller than the given limit.

   This function correctly truncates even in the presence of Unicode code
   points that encode to multi-byte encodings which must not be truncated
   in the middle.

   :param text: The (Unicode) string to truncate.
   :type text: str
   :param limit: The number of bytes to limit the UTF8 encoding to.
   :type limit: int
   :param encoding: Truncate the string in this encoding (default is ``utf-8``).
   :type encoding: str
   :param return_encoded: If ``True``, return the string encoded into bytes
       according to the specified encoding, else return the string as a string.
   :type return_encoded: bool

   :returns: The truncated string.
   :rtype: str or bytes


.. function:: xor(d1, d2)

   XOR two binary strings of arbitrary (equal) length.

   :param d1: The first binary string.
   :type d1: binary
   :param d2: The second binary string.
   :type d2: binary

   :returns: XOR of the binary strings (``XOR(d1, d2)``)
   :rtype: bytes


.. function:: utcstr(ts=None)

   Format UTC timestamp in ISO 8601 format.

   Note: to parse an ISO 8601 formatted string, use the **iso8601**
   module instead (e.g. ``iso8601.parse_date("2014-05-23T13:03:44.123Z")``).

   :param ts: The timestamp to format.
   :type ts: instance of :py:class:`datetime.datetime` or ``None``

   :returns: Timestamp formatted in ISO 8601 format.
   :rtype: str


.. function:: utcnow()

   Get current time in UTC as ISO 8601 string.

   :returns: Current time as string in ISO 8601 format.
   :rtype: str


.. class:: IdGenerator


   Bases: :class:`object`

   ID generator for WAMP request IDs.

   WAMP request IDs are sequential per WAMP session, starting at 1 and
   wrapping around at 2**53 (both value are inclusive [1, 2**53]).

   The upper bound **2**53** is chosen since it is the maximum integer that can be
   represented as a IEEE double such that all smaller integers are representable as well.

   Hence, IDs can be safely used with languages that use IEEE double as their
   main (or only) number type (JavaScript, Lua, etc).

   See https://github.com/wamp-proto/wamp-proto/blob/master/spec/basic.md#ids

   .. method:: next(self)

      Returns next ID.

      :returns: The next ID.
      :rtype: int


   .. method:: __next__(self)



.. function:: rid()

   Generate a new random integer ID from range **[0, 2**53]**.

   The generated ID is uniformly distributed over the whole range, doesn't have
   a period (no pseudo-random generator is used) and cryptographically strong.

   The upper bound **2**53** is chosen since it is the maximum integer that can be
   represented as a IEEE double such that all smaller integers are representable as well.

   Hence, IDs can be safely used with languages that use IEEE double as their
   main (or only) number type (JavaScript, Lua, etc).

   :returns: A random integer ID.
   :rtype: int


.. function:: id()

   Generate a new random integer ID from range **[0, 2**53]**.

   The generated ID is based on a pseudo-random number generator (Mersenne Twister,
   which has a period of 2**19937-1). It is NOT cryptographically strong, and
   hence NOT suitable to generate e.g. secret keys or access tokens.

   The upper bound **2**53** is chosen since it is the maximum integer that can be
   represented as a IEEE double such that all smaller integers are representable as well.

   Hence, IDs can be safely used with languages that use IEEE double as their
   main (or only) number type (JavaScript, Lua, etc).

   :returns: A random integer ID.
   :rtype: int


.. function:: newid(length=16)

   Generate a new random string ID.

   The generated ID is uniformly distributed and cryptographically strong. It is
   hence usable for things like secret keys and access tokens.

   :param length: The length (in chars) of the ID to generate.
   :type length: int

   :returns: A random string ID.
   :rtype: str


.. function:: generate_token(char_groups, chars_per_group, chars=None, sep=None, lower_case=False)

   Generate cryptographically strong tokens, which are strings like `M6X5-YO5W-T5IK`.
   These can be used e.g. for used-only-once activation tokens or the like.

   The returned token has an entropy of
   ``math.log(len(chars), 2.) * chars_per_group * char_groups``
   bits.

   With the default charset and 4 characters per group, ``generate_token()`` produces
   strings with the following entropy:

   ================   ===================  ========================================
   character groups    entropy (at least)  recommended use
   ================   ===================  ========================================
   2                    38 bits
   3                    57 bits            one-time activation or pairing code
   4                    76 bits            secure user password
   5                    95 bits
   6                   114 bits            globally unique serial / product code
   7                   133 bits
   ================   ===================  ========================================

   Here are some examples:

   * token(3): ``9QXT-UXJW-7R4H``
   * token(4): ``LPNN-JMET-KWEP-YK45``
   * token(6): ``NXW9-74LU-6NUH-VLPV-X6AG-QUE3``

   :param char_groups: Number of character groups (or characters if chars_per_group == 1).
   :type char_groups: int

   :param chars_per_group: Number of characters per character group (or 1 to return a token with no grouping).
   :type chars_per_group: int

   :param chars: Characters to choose from. Default is 27 character subset
       of the ISO basic Latin alphabet (see: ``DEFAULT_TOKEN_CHARS``).
   :type chars: str or None

   :param sep: When separating groups in the token, the separater string.
   :type sep: str

   :param lower_case: If ``True``, generate token in lower-case.
   :type lower_case: bool

   :returns: The generated token.
   :rtype: str


.. function:: generate_activation_code()

   Generate a one-time activation code or token of the form ``'W97F-96MJ-YGJL'``.
   The generated value is cryptographically strong and has (at least) 57 bits of entropy.

   :returns: The generated activation code.
   :rtype: str


.. function:: generate_user_password()

   Generate a secure, random user password of the form ``'kgojzi61dn5dtb6d'``.
   The generated value is cryptographically strong and has (at least) 76 bits of entropy.

   :returns: The generated password.
   :rtype: str


.. function:: generate_serial_number()

   Generate a globally unique serial / product code of the form ``'YRAC-EL4X-FQQE-AW4T-WNUV-VN6T'``.
   The generated value is cryptographically strong and has (at least) 114 bits of entropy.

   :returns: The generated serial number / product code.
   :rtype: str


.. function:: rtime()

   Precise, fast wallclock time.

   :returns: The current wallclock in seconds. Returned values are only guaranteed
      to be meaningful relative to each other.
   :rtype: float


.. class:: Stopwatch(start=True)


   Bases: :class:`object`

   Stopwatch based on walltime.

   This can be used to do code timing and uses the most precise walltime measurement
   available on the platform. This is a very light-weight object,
   so create/dispose is very cheap.

   .. method:: elapsed(self)

      Return total time elapsed in seconds during which the stopwatch was running.

      :returns: The elapsed time in seconds.
      :rtype: float


   .. method:: pause(self)

      Pauses the stopwatch and returns total time elapsed in seconds during which
      the stopwatch was running.

      :returns: The elapsed time in seconds.
      :rtype: float


   .. method:: resume(self)

      Resumes a paused stopwatch and returns total elapsed time in seconds
      during which the stopwatch was running.

      :returns: The elapsed time in seconds.
      :rtype: float


   .. method:: stop(self)

      Stops the stopwatch and returns total time elapsed in seconds during which
      the stopwatch was (previously) running.

      :returns: The elapsed time in seconds.
      :rtype: float



.. class:: Tracker(tracker, tracked)


   Bases: :class:`object`

   A key-based statistics tracker.

   .. method:: track(self, key)

      Track elapsed for key.

      :param key: Key under which to track the timing.
      :type key: str


   .. method:: diff(self, start_key, end_key, formatted=True)

      Get elapsed difference between two previously tracked keys.

      :param start_key: First key for interval (older timestamp).
      :type start_key: str
      :param end_key: Second key for interval (younger timestamp).
      :type end_key: str
      :param formatted: If ``True``, format computed time period and return string.
      :type formatted: bool

      :returns: Computed time period in seconds (or formatted string).
      :rtype: float or str


   .. method:: absolute(self, key)

      Return the UTC wall-clock time at which a tracked event occurred.

      :param key: The key
      :type key: str

      :returns: Timezone-naive datetime.
      :rtype: instance of :py:class:`datetime.datetime`


   .. method:: __getitem__(self, key)


   .. method:: __iter__(self)


   .. method:: __str__(self)

      Return str(self).



.. class:: EqualityMixin

   Bases: :class:`object`

   Mixing to add equality comparison operators to a class.

   Two objects are identical under this mixin, if and only if:

   1. both object have the same class
   2. all non-private object attributes are equal

   .. method:: __eq__(self, other)

      Compare this object to another object for equality.

      :param other: The other object to compare with.
      :type other: obj

      :returns: ``True`` iff the objects are equal.
      :rtype: bool


   .. method:: __ne__(self, other)

      Compare this object to another object for inequality.

      :param other: The other object to compare with.
      :type other: obj

      :returns: ``True`` iff the objects are not equal.
      :rtype: bool



.. class:: ObservableMixin

   Bases: :class:`object`

   Internal utility for enabling event-listeners on particular objects

   .. attribute:: _parent
      

      

   .. attribute:: _valid_events
      

      

   .. attribute:: _listeners
      

      

   .. attribute:: _results
      

      

   .. method:: set_valid_events(self, valid_events=None)

      :param valid_events: if non-None, .on() or .fire() with an event
      not listed in valid_events raises an exception.


   .. method:: _check_event(self, event)

      Internal helper. Throws RuntimeError if we have a valid_events
      list, and the given event isnt' in it. Does nothing otherwise.


   .. method:: on(self, event, handler)

      Add a handler for an event.

      :param event: the name of the event

      :param handler: a callable thats invoked when .fire() is
          called for this events. Arguments will be whatever are given
          to .fire()


   .. method:: off(self, event=None, handler=None)

      Stop listening for a single event, or all events.

      :param event: if None, remove all listeners. Otherwise, remove
          listeners for the single named event.

      :param handler: if None, remove all handlers for the named
          event; otherwise remove just the given handler.


   .. method:: fire(self, event, *args, **kwargs)

      Fire a particular event.

      :param event: the event to fire. All other args and kwargs are
          passed on to the handler(s) for the event.

      :return: a Deferred/Future gathering all async results from
          all handlers and/or parent handlers.



