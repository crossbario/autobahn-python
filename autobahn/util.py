###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", fWITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################
import inspect
import os
import time
import struct
import sys
import re
import base64
import math
import random
import binascii
import socket
import subprocess
from collections import OrderedDict

from typing import Optional
from datetime import datetime, timedelta
from pprint import pformat
from array import array

import txaio

try:
    _TLS = True
    from OpenSSL import SSL
except ImportError:
    _TLS = False


__all__ = ("public",
           "encode_truncate",
           "xor",
           "utcnow",
           "utcstr",
           "id",
           "rid",
           "newid",
           "rtime",
           "Stopwatch",
           "Tracker",
           "EqualityMixin",
           "ObservableMixin",
           "IdGenerator",
           "generate_token",
           "generate_activation_code",
           "generate_serial_number",
           "generate_user_password",
           "machine_id",
           'parse_keyfile',
           'write_keyfile',
           "hl",
           "hltype",
           "hlid",
           "hluserid",
           "hlval",
           "hlcontract",
           "with_0x",
           "without_0x")


def public(obj):
    """
    The public user API of Autobahn is marked using this decorator.
    Everything that is not decorated @public is library internal, can
    change at any time and should not be used in user program code.
    """
    try:
        obj._is_public = True
    except AttributeError:
        # FIXME: exceptions.AttributeError: 'staticmethod' object has no attribute '_is_public'
        pass
    return obj


@public
def encode_truncate(text, limit, encoding='utf8', return_encoded=True):
    """
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
    """
    assert(text is None or type(text) == str)
    assert(type(limit) == int)
    assert(limit >= 0)

    if text is None:
        return

    # encode the given string in the specified encoding
    s = text.encode(encoding)

    # when the resulting byte string is longer than the given limit ..
    if len(s) > limit:
        # .. truncate, and
        s = s[:limit]

        # decode back, ignoring errors that result from truncation
        # in the middle of multi-byte encodings
        text = s.decode(encoding, 'ignore')

        if return_encoded:
            s = text.encode(encoding)

    if return_encoded:
        return s
    else:
        return text


@public
def xor(d1: bytes, d2: bytes) -> bytes:
    """
    XOR two binary strings of arbitrary (equal) length.

    :param d1: The first binary string.
    :param d2: The second binary string.

    :returns: XOR of the binary strings (``XOR(d1, d2)``)
    """
    if type(d1) != bytes:
        raise Exception("invalid type {} for d1 - must be binary".format(type(d1)))
    if type(d2) != bytes:
        raise Exception("invalid type {} for d2 - must be binary".format(type(d2)))
    if len(d1) != len(d2):
        raise Exception("cannot XOR binary string of differing length ({} != {})".format(len(d1), len(d2)))

    d1 = array('B', d1)
    d2 = array('B', d2)

    for i in range(len(d1)):
        d1[i] ^= d2[i]

    return d1.tobytes()


@public
def utcstr(ts=None):
    """
    Format UTC timestamp in ISO 8601 format.

    Note: to parse an ISO 8601 formatted string, use the **iso8601**
    module instead (e.g. ``iso8601.parse_date("2014-05-23T13:03:44.123Z")``).

    >>> txaio.time_ns()
    1641121311914026419
    >>> int(iso8601.parse_date(utcnow()).timestamp() * 1000000000.)
    1641121313209000192

    :param ts: The timestamp to format.
    :type ts: instance of :py:class:`datetime.datetime` or ``None``

    :returns: Timestamp formatted in ISO 8601 format.
    :rtype: str
    """
    assert(ts is None or isinstance(ts, datetime))
    if ts is None:
        ts = datetime.utcnow()
    return "{0}Z".format(ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3])


@public
def utcnow():
    """
    Get current time in UTC as ISO 8601 string.

    :returns: Current time as string in ISO 8601 format.
    :rtype: str
    """
    return utcstr()


class IdGenerator(object):
    """
    ID generator for WAMP request IDs.

    WAMP request IDs are sequential per WAMP session, starting at 1 and
    wrapping around at 2**53 (both value are inclusive [1, 2**53]).

    The upper bound **2**53** is chosen since it is the maximum integer that can be
    represented as a IEEE double such that all smaller integers are representable as well.

    Hence, IDs can be safely used with languages that use IEEE double as their
    main (or only) number type (JavaScript, Lua, etc).

    See https://github.com/wamp-proto/wamp-proto/blob/master/spec/basic.md#ids
    """

    def __init__(self):
        self._next = 0  # starts at 1; next() pre-increments

    def next(self):
        """
        Returns next ID.

        :returns: The next ID.
        :rtype: int
        """
        self._next += 1
        if self._next > 9007199254740992:
            self._next = 1
        return self._next

    # generator protocol
    def __next__(self):
        return self.next()


#
# Performance comparison of IdGenerator.next(), id() and rid().
#
# All tests were performed on:
#
#   - Ubuntu 14.04 LTS x86-64
#   - Intel Core i7 920 @ 3.3GHz
#
# The tests generated 100 mio. IDs and run-time was measured
# as wallclock from Unix "time" command. In each run, a single CPU
# core was essentially at 100% load all the time (though the sys/usr
# ratio was different).
#
# PyPy 2.6.1:
#
#   IdGenerator.next()    0.5s
#   id()                 29.4s
#   rid()               106.1s
#
# CPython 2.7.10:
#
#   IdGenerator.next()   49.0s
#   id()                370.5s
#   rid()               196.4s
#

#
# Note on the ID range [0, 2**53]. We once reduced the range to [0, 2**31].
# This lead to extremely hard to track down issues due to ID collisions!
# Here: https://github.com/crossbario/autobahn-python/issues/419#issue-90483337
#


# 8 byte mask with 53 LSBs set (WAMP requires IDs from [0, 2**53]
_WAMP_ID_MASK = struct.unpack(">Q", b"\x00\x1f\xff\xff\xff\xff\xff\xff")[0]


def rid():
    """
    Generate a new random integer ID from range **[0, 2**53]**.

    The generated ID is uniformly distributed over the whole range, doesn't have
    a period (no pseudo-random generator is used) and cryptographically strong.

    The upper bound **2**53** is chosen since it is the maximum integer that can be
    represented as a IEEE double such that all smaller integers are representable as well.

    Hence, IDs can be safely used with languages that use IEEE double as their
    main (or only) number type (JavaScript, Lua, etc).

    :returns: A random integer ID.
    :rtype: int
    """
    return struct.unpack("@Q", os.urandom(8))[0] & _WAMP_ID_MASK


# noinspection PyShadowingBuiltins
def id():
    """
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
    """
    return random.randint(0, 9007199254740992)


def newid(length=16):
    """
    Generate a new random string ID.

    The generated ID is uniformly distributed and cryptographically strong. It is
    hence usable for things like secret keys and access tokens.

    :param length: The length (in chars) of the ID to generate.
    :type length: int

    :returns: A random string ID.
    :rtype: str
    """
    l = int(math.ceil(float(length) * 6. / 8.))
    return base64.b64encode(os.urandom(l))[:length].decode('ascii')


# a standard base36 character set
# DEFAULT_TOKEN_CHARS = string.digits + string.ascii_uppercase

# we take out the following 9 chars (leaving 27), because there
# is visual ambiguity: 0/O/D, 1/I, 8/B, 2/Z
DEFAULT_TOKEN_CHARS = '345679ACEFGHJKLMNPQRSTUVWXY'
"""
Default set of characters to create rtokens from.
"""

DEFAULT_ZBASE32_CHARS = '13456789abcdefghijkmnopqrstuwxyz'
"""
Our choice of confusing characters to eliminate is: `0', `l', `v', and `2'.  Our
reasoning is that `0' is potentially mistaken for `o', that `l' is potentially
mistaken for `1' or `i', that `v' is potentially mistaken for `' or `r'
(especially in handwriting) and that `2' is potentially mistaken for `z'
(especially in handwriting).

Note that we choose to focus on typed and written transcription more than on
vocal, since humans already have a well-established system of disambiguating
spoken alphanumerics, such as the United States military's "Alpha Bravo Charlie
Delta" and telephone operators' "Is that 'd' as in 'dog'?".

* http://philzimmermann.com/docs/human-oriented-base-32-encoding.txt
"""


@public
def generate_token(char_groups: int,
                   chars_per_group: int,
                   chars: Optional[str] = None,
                   sep: Optional[str] = None,
                   lower_case: Optional[bool] = False) -> str:
    """
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
    :param chars_per_group: Number of characters per character group (or 1 to return a token with no grouping).
    :param chars: Characters to choose from. Default is 27 character subset
        of the ISO basic Latin alphabet (see: ``DEFAULT_TOKEN_CHARS``).
    :param sep: When separating groups in the token, the separater string.
    :param lower_case: If ``True``, generate token in lower-case.

    :returns: The generated token.
    """
    assert(type(char_groups) == int)
    assert(type(chars_per_group) == int)
    assert(chars is None or type(chars) == str), 'chars must be str, was {}'.format(type(chars))
    chars = chars or DEFAULT_TOKEN_CHARS
    if lower_case:
        chars = chars.lower()
    sep = sep or '-'
    rng = random.SystemRandom()
    token_value = ''.join(rng.choice(chars) for _ in range(char_groups * chars_per_group))
    if chars_per_group > 1:
        return sep.join(map(''.join, zip(*[iter(token_value)] * chars_per_group)))
    else:
        return token_value


@public
def generate_activation_code():
    """
    Generate a one-time activation code or token of the form ``'W97F-96MJ-YGJL'``.
    The generated value is cryptographically strong and has (at least) 57 bits of entropy.

    :returns: The generated activation code.
    :rtype: str
    """
    return generate_token(char_groups=3, chars_per_group=4, chars=DEFAULT_TOKEN_CHARS, sep='-', lower_case=False)


_PAT_ACTIVATION_CODE = re.compile('^([' + DEFAULT_TOKEN_CHARS + ']{4,4})-([' + DEFAULT_TOKEN_CHARS + ']{4,4})-([' + DEFAULT_TOKEN_CHARS + ']{4,4})$')


@public
def parse_activation_code(code: str):
    """
    Parse an activation code generated by :func:<autobahn.util.generate_activation_code>:

    .. code:: console

        "RWCN-94NV-CEHR" -> ("RWCN", "94NV", "CEHR") | None

    :param code: The code to parse, e.g. ``'W97F-96MJ-YGJL'``.
    :return: If the string is a properly conforming activation code, return
        the matched pattern, otherwise return ``None``.
    """
    return _PAT_ACTIVATION_CODE.match(code)


@public
def generate_user_password():
    """
    Generate a secure, random user password of the form ``'kgojzi61dn5dtb6d'``.
    The generated value is cryptographically strong and has (at least) 76 bits of entropy.

    :returns: The generated password.
    :rtype: str
    """
    return generate_token(char_groups=16, chars_per_group=1, chars=DEFAULT_ZBASE32_CHARS, sep='-', lower_case=True)


@public
def generate_serial_number():
    """
    Generate a globally unique serial / product code of the form ``'YRAC-EL4X-FQQE-AW4T-WNUV-VN6T'``.
    The generated value is cryptographically strong and has (at least) 114 bits of entropy.

    :returns: The generated serial number / product code.
    :rtype: str
    """
    return generate_token(char_groups=6, chars_per_group=4, chars=DEFAULT_TOKEN_CHARS, sep='-', lower_case=False)


# Select the most precise walltime measurement function available
# on the platform
#
if sys.platform.startswith('win'):
    # On Windows, this function returns wall-clock seconds elapsed since the
    # first call to this function, as a floating point number, based on the
    # Win32 function QueryPerformanceCounter(). The resolution is typically
    # better than one microsecond
    if sys.version_info >= (3, 8):
        _rtime = time.perf_counter
    else:
        _rtime = time.clock
    _ = _rtime()  # this starts wallclock
else:
    # On Unix-like platforms, this used the first available from this list:
    # (1) gettimeofday() -- resolution in microseconds
    # (2) ftime() -- resolution in milliseconds
    # (3) time() -- resolution in seconds
    _rtime = time.time


@public
def rtime():
    """
    Precise, fast wallclock time.

    :returns: The current wallclock in seconds. Returned values are only guaranteed
       to be meaningful relative to each other.
    :rtype: float
    """
    return _rtime()


class Stopwatch(object):
    """
    Stopwatch based on walltime.

    This can be used to do code timing and uses the most precise walltime measurement
    available on the platform. This is a very light-weight object,
    so create/dispose is very cheap.
    """

    def __init__(self, start=True):
        """

        :param start: If ``True``, immediately start the stopwatch.
        :type start: bool
        """
        self._elapsed = 0
        if start:
            self._started = rtime()
            self._running = True
        else:
            self._started = None
            self._running = False

    def elapsed(self):
        """
        Return total time elapsed in seconds during which the stopwatch was running.

        :returns: The elapsed time in seconds.
        :rtype: float
        """
        if self._running:
            now = rtime()
            return self._elapsed + (now - self._started)
        else:
            return self._elapsed

    def pause(self):
        """
        Pauses the stopwatch and returns total time elapsed in seconds during which
        the stopwatch was running.

        :returns: The elapsed time in seconds.
        :rtype: float
        """
        if self._running:
            now = rtime()
            self._elapsed += now - self._started
            self._running = False
            return self._elapsed
        else:
            return self._elapsed

    def resume(self):
        """
        Resumes a paused stopwatch and returns total elapsed time in seconds
        during which the stopwatch was running.

        :returns: The elapsed time in seconds.
        :rtype: float
        """
        if not self._running:
            self._started = rtime()
            self._running = True
            return self._elapsed
        else:
            now = rtime()
            return self._elapsed + (now - self._started)

    def stop(self):
        """
        Stops the stopwatch and returns total time elapsed in seconds during which
        the stopwatch was (previously) running.

        :returns: The elapsed time in seconds.
        :rtype: float
        """
        elapsed = self.pause()
        self._elapsed = 0
        self._started = None
        self._running = False
        return elapsed


class Tracker(object):
    """
    A key-based statistics tracker.
    """

    def __init__(self, tracker, tracked):
        """
        """
        self.tracker = tracker
        self.tracked = tracked
        self._timings = {}
        self._offset = rtime()
        self._dt_offset = datetime.utcnow()

    def track(self, key):
        """
        Track elapsed for key.

        :param key: Key under which to track the timing.
        :type key: str
        """
        self._timings[key] = rtime()

    def diff(self, start_key, end_key, formatted=True):
        """
        Get elapsed difference between two previously tracked keys.

        :param start_key: First key for interval (older timestamp).
        :type start_key: str
        :param end_key: Second key for interval (younger timestamp).
        :type end_key: str
        :param formatted: If ``True``, format computed time period and return string.
        :type formatted: bool

        :returns: Computed time period in seconds (or formatted string).
        :rtype: float or str
        """
        if end_key in self._timings and start_key in self._timings:
            d = self._timings[end_key] - self._timings[start_key]
            if formatted:
                if d < 0.00001:  # 10us
                    s = "%d ns" % round(d * 1000000000.)
                elif d < 0.01:  # 10ms
                    s = "%d us" % round(d * 1000000.)
                elif d < 10:  # 10s
                    s = "%d ms" % round(d * 1000.)
                else:
                    s = "%d s" % round(d)
                return s.rjust(8)
            else:
                return d
        else:
            if formatted:
                return "n.a.".rjust(8)
            else:
                return None

    def absolute(self, key):
        """
        Return the UTC wall-clock time at which a tracked event occurred.

        :param key: The key
        :type key: str

        :returns: Timezone-naive datetime.
        :rtype: instance of :py:class:`datetime.datetime`
        """
        elapsed = self[key]
        if elapsed is None:
            raise KeyError("No such key \"%s\"." % elapsed)
        return self._dt_offset + timedelta(seconds=elapsed)

    def __getitem__(self, key):
        if key in self._timings:
            return self._timings[key] - self._offset
        else:
            return None

    def __iter__(self):
        return self._timings.__iter__()

    def __str__(self):
        return pformat(self._timings)


class EqualityMixin(object):
    """
    Mixing to add equality comparison operators to a class.

    Two objects are identical under this mixin, if and only if:

    1. both object have the same class
    2. all non-private object attributes are equal
    """

    def __eq__(self, other):
        """
        Compare this object to another object for equality.

        :param other: The other object to compare with.
        :type other: obj

        :returns: ``True`` iff the objects are equal.
        :rtype: bool
        """
        if not isinstance(other, self.__class__):
            return False
        # we only want the actual message data attributes (not eg _serialize)
        for k in self.__dict__:
            if not k.startswith('_'):
                if not self.__dict__[k] == other.__dict__[k]:
                    return False
        return True
        # return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        """
        Compare this object to another object for inequality.

        :param other: The other object to compare with.
        :type other: obj

        :returns: ``True`` iff the objects are not equal.
        :rtype: bool
        """
        return not self.__eq__(other)


def wildcards2patterns(wildcards):
    """
    Compute a list of regular expression patterns from a list of
    wildcard strings. A wildcard string uses '*' as a wildcard character
    matching anything.

    :param wildcards: List of wildcard strings to compute regular expression patterns for.
    :type wildcards: list of str

    :returns: Computed regular expressions.
    :rtype: list of obj
    """
    # note that we add the ^ and $ so that the *entire* string must
    # match. Without this, e.g. a prefix will match:
    # re.match('.*good\\.com', 'good.com.evil.com')  # match!
    # re.match('.*good\\.com$', 'good.com.evil.com') # no match!
    return [re.compile('^' + wc.replace('.', r'\.').replace('*', '.*') + '$') for wc in wildcards]


class ObservableMixin(object):
    """
    Internal utility for enabling event-listeners on particular objects
    """

    # A "helper" style composable class (as opposed to a mix-in) might
    # be a lot easier to deal with here.  Having an __init__ method
    # with a "mix in" style class can be fragile and error-prone,
    # especially if it takes arguments. Since we don't use the
    # "parent" beavior anywhere, I didn't add a .set_parent() (yet?)

    # these are class-level globals; individual instances are
    # initialized as-needed (e.g. the first .on() call adds a
    # _listeners dict). Thus, subclasses don't have to call super()
    # properly etc.
    _parent = None
    _valid_events = None
    _listeners = None
    _results = None

    def set_valid_events(self, valid_events=None):
        """
        :param valid_events: if non-None, .on() or .fire() with an event
            not listed in valid_events raises an exception.
        """
        self._valid_events = list(valid_events)
        self._results = {k: None for k in self._valid_events}

    def _check_event(self, event):
        """
        Internal helper. Throws RuntimeError if we have a valid_events
        list, and the given event isnt' in it. Does nothing otherwise.
        """
        if self._valid_events and event not in self._valid_events:
            raise RuntimeError(
                "Invalid event '{event}'. Expected one of: {events}".format(
                    event=event,
                    events=', '.join(self._valid_events),
                )
            )

    def on(self, event, handler):
        """
        Add a handler for an event.

        :param event: the name of the event

        :param handler: a callable thats invoked when .fire() is
            called for this events. Arguments will be whatever are given
            to .fire()
        """
        # print("adding '{}' to '{}': {}".format(event, hash(self), handler))
        self._check_event(event)
        if self._listeners is None:
            self._listeners = dict()
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(handler)

    def off(self, event=None, handler=None):
        """
        Stop listening for a single event, or all events.

        :param event: if None, remove all listeners. Otherwise, remove
            listeners for the single named event.

        :param handler: if None, remove all handlers for the named
            event; otherwise remove just the given handler.
        """
        if event is None:
            if handler is not None:
                # maybe this should mean "remove the given handler
                # from any event at all that contains it"...?
                raise RuntimeError(
                    "Can't specificy a specific handler without an event"
                )
            self._listeners = dict()
        else:
            if self._listeners is None:
                return
            self._check_event(event)
            if event in self._listeners:
                if handler is None:
                    del self._listeners[event]
                else:
                    try:
                        self._listeners[event].remove(handler)
                    except ValueError:
                        pass

    def fire(self, event, *args, **kwargs):
        """
        Fire a particular event.

        :param event: the event to fire. All other args and kwargs are
            passed on to the handler(s) for the event.

        :return: a Deferred/Future gathering all async results from
            all handlers and/or parent handlers.
        """
        # print("firing '{}' from '{}'".format(event, hash(self)))
        if self._listeners is None:
            return txaio.create_future(result=[])

        self._check_event(event)
        res = []
        for handler in self._listeners.get(event, []):
            future = txaio.as_future(handler, *args, **kwargs)
            res.append(future)
        if self._parent is not None:
            res.append(self._parent.fire(event, *args, **kwargs))
        d_res = txaio.gather(res, consume_exceptions=False)
        self._results[event] = d_res
        return d_res


class _LazyHexFormatter(object):
    """
    This is used to avoid calling binascii.hexlify() on data given to
    log.debug() calls unless debug is active (for example). Like::

        self.log.debug(
            "Some data: {octets}",
            octets=_LazyHexFormatter(os.urandom(32)),
        )
    """
    __slots__ = ('obj',)

    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return binascii.hexlify(self.obj).decode('ascii')


def _is_tls_error(instance):
    """
    :returns: True if we have TLS support and 'instance' is an
        instance of :class:`OpenSSL.SSL.Error` otherwise False
    """
    if _TLS:
        return isinstance(instance, SSL.Error)
    return False


def _maybe_tls_reason(instance):
    """
    :returns: a TLS error-message, or empty-string if 'instance' is
        not a TLS error.
    """
    if _is_tls_error(instance):
        ssl_error = instance.args[0][0]
        return "SSL error: {msg} (in {func})".format(
            func=ssl_error[1],
            msg=ssl_error[2],
        )
    return ""


def machine_id() -> str:
    """
    For informational purposes, get a unique ID or serial for this machine (device).

    :returns: Unique machine (device) ID (serial), e.g. ``81655b901e334fc1ad59cbf2719806b7``.
    """
    from twisted.python.runtime import platform

    if platform.isLinux():
        try:
            # why this? see: http://0pointer.de/blog/projects/ids.html
            with open('/var/lib/dbus/machine-id', 'r') as f:
                return f.read().strip()
        except:
            # Non-dbus using Linux, get a hostname
            return socket.gethostname()
    elif platform.isMacOSX():
        import plistlib
        plist_data = subprocess.check_output(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice", "-a"])
        return plistlib.loads(plist_data)[0]["IOPlatformSerialNumber"]
    else:
        return socket.gethostname()


try:
    import click
    _HAS_CLICK = True
except ImportError:
    _HAS_CLICK = False


def hl(text, bold=False, color='yellow'):
    if not isinstance(text, str):
        text = '{}'.format(text)
    if _HAS_CLICK:
        return click.style(text, fg=color, bold=bold)
    else:
        return text


def _qn(obj):
    if inspect.isclass(obj) or inspect.isfunction(obj) or inspect.ismethod(obj):
        qn = '{}.{}'.format(obj.__module__, obj.__qualname__)
    else:
        qn = 'unknown'
    return qn


def hltype(obj):
    qn = _qn(obj).split('.')
    text = hl(qn[0], color='yellow', bold=True) + hl('.' + '.'.join(qn[1:]), color='yellow', bold=False)
    return '<' + text + '>'


def hlid(oid):
    return hl('{}'.format(oid), color='blue', bold=True)


def hluserid(oid):
    if not isinstance(oid, str):
        oid = '{}'.format(oid)
    return hl('"{}"'.format(oid), color='yellow', bold=True)


def hlval(val, color='white', bold=True):
    return hl('{}'.format(val), color=color, bold=bold)


def hlcontract(oid):
    if not isinstance(oid, str):
        oid = '{}'.format(oid)
    return hl('<{}>'.format(oid), color='magenta', bold=True)


def with_0x(address):
    if address and not address.startswith('0x'):
        return '0x{address}'.format(address=address)
    return address


def without_0x(address):
    if address and address.startswith('0x'):
        return address[2:]
    return address


def write_keyfile(filepath, tags, msg):
    """
    Internal helper, write the given tags to the given file-
    """
    with open(filepath, 'w') as f:
        f.write(msg)
        for (tag, value) in tags.items():
            if value:
                f.write('{}: {}\n'.format(tag, value))


def parse_keyfile(key_path: str, private: bool = True) -> OrderedDict:
    """
    Internal helper. This parses a node.pub or node.priv file and
    returns a dict mapping tags -> values.
    """
    if os.path.exists(key_path) and not os.path.isfile(key_path):
        raise Exception("Key file '{}' exists, but isn't a file".format(key_path))

    allowed_tags = [
        # common tags
        'public-key-ed25519',
        'public-adr-eth',
        'created-at',
        'creator',

        # user profile
        'user-id',

        # node profile
        'machine-id',
        'node-authid',
        'node-cluster-ip',
    ]

    if private:
        # private key file tags
        allowed_tags.extend(['private-key-ed25519', 'private-key-eth'])

    tags = OrderedDict()  # type: ignore
    with open(key_path, 'r') as key_file:
        got_blankline = False
        for line in key_file.readlines():
            if line.strip() == '':
                got_blankline = True
            elif got_blankline:
                tag, value = line.split(':', 1)
                tag = tag.strip().lower()
                value = value.strip()
                if tag not in allowed_tags:
                    raise Exception("Invalid tag '{}' in key file {}".format(tag, key_path))
                if tag in tags:
                    raise Exception("Duplicate tag '{}' in key file {}".format(tag, key_path))
                tags[tag] = value
    return tags
