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

from autobahn.wamp.uri import Pattern


def register(uri):
    """
    Decorator for WAMP procedure endpoints.
    """
    def decorate(f):
        assert(callable(f))
        if not hasattr(f, '_wampuris'):
            f._wampuris = []
        f._wampuris.append(Pattern(uri, Pattern.URI_TARGET_ENDPOINT))
        return f
    return decorate


def subscribe(uri):
    """
    Decorator for WAMP event handlers.
    """
    def decorate(f):
        assert(callable(f))
        if not hasattr(f, '_wampuris'):
            f._wampuris = []
        f._wampuris.append(Pattern(uri, Pattern.URI_TARGET_HANDLER))
        return f
    return decorate


def error(uri):
    """
    Decorator for WAMP error classes.
    """
    def decorate(cls):
        assert(issubclass(cls, Exception))
        if not hasattr(cls, '_wampuris'):
            cls._wampuris = []
        cls._wampuris.append(Pattern(uri, Pattern.URI_TARGET_EXCEPTION))
        return cls
    return decorate
