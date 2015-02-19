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

# http://docs.python.org/2/library/inspect.html
# https://github.com/dotcloud/zerorpc-python/blob/master/zerorpc/decorators.py

import inspect
import asyncio


class Foo(object):
    pass


@asyncio.coroutine
def add2(a, b=3, c=Foo, d="klj", *args, **kwargs):
    """
    Adds 2 numbers.

    :param a: First number.
    :type a: int
    :param b: Second number.
    :type b: int
    :returns: int -- The sum of both numbers.
    """
    return a + b


def get_class_default_arg(fn, klass):
    argspec = inspect.getargspec(fn)
    if argspec and argspec.defaults:
        for i in range(len(argspec.defaults)):
            if argspec.defaults[-i] == klass:
                return argspec.args[-i]
    return None

print(inspect.signature(add2))
print(inspect.getargspec(add2))
print(get_class_default_arg(add2, Foo))
print(inspect.cleandoc(add2.__doc__))
