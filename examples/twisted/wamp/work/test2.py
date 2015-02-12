
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
