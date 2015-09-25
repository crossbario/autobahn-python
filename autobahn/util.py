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

import txaio


__all__ = ("utcnow",
           "utcstr",
           "id",
           "rid",
           "newid",
           "rtime",
           "Stopwatch",
           "Tracker",
           "EqualityMixin",
           "ObservableMixin",
           "IdGenerator")


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

    WAMP request IDs are sequential per WAMP session, starting at 0 and
    wrapping around at 2**53 (both value are inclusive [0, 2**53]).

    The upper bound **2**53** is chosen since it is the maximum integer that can be
    represented as a IEEE double such that all smaller integers are representable as well.

    Hence, IDs can be safely used with languages that use IEEE double as their
    main (or only) number type (JavaScript, Lua, etc).

    See https://github.com/tavendo/WAMP/blob/master/spec/basic.md#ids
    """

    def __init__(self):
        self._next = -1

    def next(self):
        """
        Returns next ID.

        :returns: The next ID.
        :rtype: int
        """
        self._next += 1
        if self._next > 9007199254740992:
            self._next = 0
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
# Here: https://github.com/tavendo/AutobahnPython/issues/419#issue-90483337
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


# XXX I really think this would be better as a helper object rather
# than a mix-in ... and fit the "composition over inheritance" theme
# ;)

# XXX also, it *really* needs to know what the valid events are so a
# proper error message can happen if you .on/.off on something bogus
# (e.g. fat-finger "jion" instead of "join" and then nothing works)
class ObservableMixin(object):

    def __init__(self, valid_events, parent=None):
        self._valid_events = valid_events
        self._parent = parent
        self._listeners = {}

    def on(self, event, handler):
        if event not in self._valid_events:
            raise Exception("Invalid event '{0}'".format(event))
        if event not in self._listeners:
            self._listeners[event] = set()
        self._listeners[event].add(handler)

    def off(self, event=None, handler=None):
        if event is None:
            self._listeners = {}
        else:
            if event not in self._valid_events:
                raise Exception("Invalid event '{0}'".format(event))
            if event in self._listeners:
                if handler is None:
                    del self._listeners[event]
                else:
                    self._listeners[event].discard(handler)

    def _error(self, fail):
        self.log.error("event notification failed: {fail}", fail=txaio.failure_format_traceback(fail))
        return None

    # XXX should probably be _fire (e.g. private)
    def fire(self, event, *args, **kwargs):
        res = []
        if event in self._listeners:
            for handler in self._listeners[event]:
                try:
                    d = txaio.as_future(handler, *args, **kwargs)
                    txaio.add_callbacks(d, None, self._error)
                    res.append(d)
                except Exception:
                    # this better? res.append(txaio.create_future_error())
                    return txaio.create_future_error()
        if self._parent is not None:
            res.append(self._parent.fire(event, *args, **kwargs))

        # otherwise, we'll return a list of tuples of the events'
        # results; probably not what's intended?
        def return_none(arg):
            return None
        d = txaio.gather(res, consume_exceptions=False)
        txaio.add_callbacks(d, return_none, None)
