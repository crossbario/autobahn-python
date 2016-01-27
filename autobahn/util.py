###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
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
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from __future__ import absolute_import

import os
import time
import struct
import sys
import re
import base64
import math
import random
from datetime import datetime, timedelta
from pprint import pformat
from array import array

import six

import txaio


__all__ = ("xor",
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
           "generate_user_password")


def xor(d1, d2):
    """
    XOR two binary strings of arbitrary (equal) length.

    :param d1: The first binary string.
    :type d1: binary
    :param d2: The second binary string.
    :type d2: binary

    :returns: XOR(d1, d2)
    :rtype: binary
    """
    if type(d1) != six.binary_type:
        raise Exception("invalid type {} for d1 - must be binary".format(type(d1)))
    if type(d2) != six.binary_type:
        raise Exception("invalid type {} for d2 - must be binary".format(type(d2)))
    if len(d1) != len(d2):
        raise Exception("cannot XOR binary string of differing length ({} != {})".format(len(d1), len(d2)))

    d1 = array('B', d1)
    d2 = array('B', d2)

    for i in range(len(d1)):
        d1[i] ^= d2[i]

    if six.PY3:
        return d1.tobytes()
    else:
        return d1.tostring()


def utcstr(ts=None):
    """
    Format UTC timestamp in ISO 8601 format.

    Note: to parse an ISO 8601 formatted string, use the **iso8601**
    module instead (e.g. ``iso8601.parse_date("2014-05-23T13:03:44.123Z")``).

    :param ts: The timestamp to format.
    :type ts: instance of :py:class:`datetime.datetime` or None

    :returns: Timestamp formatted in ISO 8601 format.
    :rtype: unicode
    """
    assert(ts is None or isinstance(ts, datetime))
    if ts is None:
        ts = datetime.utcnow()
    return u"{0}Z".format(ts.strftime(u"%Y-%m-%dT%H:%M:%S.%f")[:-3])


def utcnow():
    """
    Get current time in UTC as ISO 8601 string.

    :returns: Current time as string in ISO 8601 format.
    :rtype: unicode
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
    :rtype: unicode
    """
    l = int(math.ceil(float(length) * 6. / 8.))
    return base64.b64encode(os.urandom(l))[:length].decode('ascii')


# a standard base36 character set
# DEFAULT_TOKEN_CHARS = string.digits + string.ascii_uppercase

# we take out the following 9 chars (leaving 27), because there
# is visual ambiguity: 0/O/D, 1/I, 8/B, 2/Z
DEFAULT_TOKEN_CHARS = u'345679ACEFGHJKLMNPQRSTUVWXY'
"""
Default set of characters to create rtokens from.
"""

DEFAULT_ZBASE32_CHARS = u'13456789abcdefghijkmnopqrstuwxyz'
"""
http://philzimmermann.com/docs/human-oriented-base-32-encoding.txt

Our choice of confusing characters to eliminate is: `0', `l', `v', and `2'.  Our
reasoning is that `0' is potentially mistaken for `o', that `l' is potentially
mistaken for `1' or `i', that `v' is potentially mistaken for `u' or `r'
(especially in handwriting) and that `2' is potentially mistaken for `z'
(especially in handwriting).

Note that we choose to focus on typed and written transcription more than on
vocal, since humans already have a well-established system of disambiguating
spoken alphanumerics, such as the United States military's "Alpha Bravo Charlie
Delta" and telephone operators' "Is that 'd' as in 'dog'?".
"""


def generate_token(char_groups, chars_per_group, chars=None, sep=None, lower_case=False):
    """
    Generate cryptographically strong tokens, which are strings like `M6X5-YO5W-T5IK`.
    These can be used e.g. for used-only-once activation tokens or the like.

    The returned token has an entropy of:

       math.log(len(chars), 2.) * chars_per_group * char_groups

    bits. With the default charset and 4 characters per group, rtoken() produces
    tokens with the following entropy:

        character groups    entropy (at least)  recommended use

        2                    38 bits
        3                    57 bits            one-time activation or pairing code
        4                    76 bits            secure user password
        5                    95 bits
        6                   114 bits            globally unique serial / product code
        7                   133 bits

    Here are 3 examples:

        * token(3): 9QXT-UXJW-7R4H
        * token(4): LPNN-JMET-KWEP-YK45
        * token(6): NXW9-74LU-6NUH-VLPV-X6AG-QUE3

    :param char_groups: Number of character groups (or characters if chars_per_group == 1).
    :type char_groups: int
    :param chars_per_group: Number of characters per character group (or 1 to return a token with no grouping).
    :type chars_per_group: int
    :param chars: Characters to choose from. Default is 27 character subset
        of the ISO basic Latin alphabet (see: DEFAULT_TOKEN_CHARS).
    :type chars: unicode or None
    :param sep: When separating groups in the token, the separater string.
    :type sep: unicode

    :returns: The generated token.
    :rtype: unicode
    """
    assert(type(char_groups) in six.integer_types)
    assert(type(chars_per_group) in six.integer_types)
    assert(chars is None or type(chars) == six.text_type)
    chars = chars or DEFAULT_TOKEN_CHARS
    if lower_case:
        chars = chars.lower()
    sep = sep or u'-'
    rng = random.SystemRandom()
    token_value = u''.join(rng.choice(chars) for _ in range(char_groups * chars_per_group))
    if chars_per_group > 1:
        return sep.join(map(u''.join, zip(*[iter(token_value)] * chars_per_group)))
    else:
        return token_value


def generate_activation_code():
    return generate_token(char_groups=3, chars_per_group=4, chars=DEFAULT_TOKEN_CHARS, sep=u'-', lower_case=False)


def generate_user_password():
    return generate_token(char_groups=16, chars_per_group=1, chars=DEFAULT_ZBASE32_CHARS, sep=u'-', lower_case=True)


def generate_serial_number():
    return generate_token(char_groups=6, chars_per_group=4, chars=DEFAULT_TOKEN_CHARS, sep=u'-', lower_case=False)


# Select the most precise walltime measurement function available
# on the platform
#
if sys.platform.startswith('win'):
    # On Windows, this function returns wall-clock seconds elapsed since the
    # first call to this function, as a floating point number, based on the
    # Win32 function QueryPerformanceCounter(). The resolution is typically
    # better than one microsecond
    _rtime = time.clock
    _ = _rtime()  # this starts wallclock
else:
    # On Unix-like platforms, this used the first available from this list:
    # (1) gettimeofday() -- resolution in microseconds
    # (2) ftime() -- resolution in milliseconds
    # (3) time() -- resolution in seconds
    _rtime = time.time


rtime = _rtime
"""
Precise wallclock time.

:returns: The current wallclock in seconds. Returned values are only guaranteed
   to be meaningful relative to each other.
:rtype: float
"""


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
    return [re.compile(wc.replace('.', '\.').replace('*', '.*')) for wc in wildcards]


class ObservableMixin(object):

    def __init__(self, parent=None):
        self._parent = parent
        self._listeners = {}

    def on(self, event, handler):
        if event not in self._listeners:
            self._listeners[event] = set()
        self._listeners[event].add(handler)

    def off(self, event=None, handler=None):
        if event is None:
            self._listeners = {}
        else:
            if event in self._listeners:
                if handler is None:
                    del self._listeners[event]
                else:
                    self._listeners[event].discard(handler)

    def fire(self, event, *args, **kwargs):
        res = []
        if event in self._listeners:
            for handler in self._listeners[event]:
                value = txaio.as_future(handler, *args, **kwargs)
                res.append(value)
        if self._parent is not None:
            res.append(self._parent.fire(event, *args, **kwargs))
        return txaio.gather(res)
