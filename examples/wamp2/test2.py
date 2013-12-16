
# http://docs.python.org/2/library/inspect.html
# https://github.com/dotcloud/zerorpc-python/blob/master/zerorpc/decorators.py

import inspect

def add2(a, b = 3, *args, **kwargs):
   """
   Adds 2 numbers.

   :param a: First number.
   :type a: int
   :param b: Second number.
   :type b: int
   :returns: int -- The sum of both numbers.
   """
   return a + b


print inspect.getargspec(add2)
print inspect.cleandoc(add2.__doc__)
