###############################################################################
#
#  Copyright (C) 2014 Tavendo GmbH
#  Copyright (C) 2014 Christian Kampka <christian@kampka.net>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###############################################################################

try:
   import asyncio
   from asyncio import Future, iscoroutine
except ImportError:
   ## Trollius >= 0.3 was renamed
   # noinspection PyUnresolvedReferences
   import trollius as asyncio
   from trollius import Future, iscoroutine

from autobahn.asyncio.log import LogMixin

__all__ = ("LoopMixin", )

class FutureMixin:
   """
   Mixin for Asyncio style Futures.
   """

   @staticmethod
   def create_future():
      """
      Creates a new asyncio future
      """
      return Future()

   @staticmethod
   def as_future(fun, *args, **kwargs):
      """
      Executes a function with the given arguments
      and wraps the result into a future.
      :param fun: The function to be called.
      :type fun: func
      :param args: The argument list for the supplied function.
      :type args: list
      :param kwargs: The keyword argument dict for the supplied function.
      :type kwargs: dict
      :return: The functions result wrapped in a Future
      :rtype: asyncio.Future
      """
      try:
         res = fun(*args, **kwargs)
      except Exception as e:
         f = Future()
         f.set_exception(e)
         return f
      else:
         if isinstance(res, Future):
            return res
         elif iscoroutine(res):
            return asyncio.Task(res)
         else:
            f = Future()
            f.set_result(res)
            return f

   @staticmethod
   def resolve_future(future, value):
      """
      Resolve a future sucessfully with a given value.
      :param future: The future to be resolved.
      :type future: asyncio.Future
      :param value: The value to resolve the Future with.
      :type value: any
      """
      future.set_result(value)

   @staticmethod
   def reject_future(future, exception):
      """
      Rejects a future with a given exception.
      :param future: The future to be rejected.
      :type future: asyncio.Future
      :param exception: The exception to reject the Future with.
      :type exception: Exception
      """
      future.set_exception(exception)

   @staticmethod
   def add_future_callbacks(future, callback, errback):
      """
      Register callback and errorback functions with a Future.
      :param future: The future to register callbacks with.
      :type future: asyncio.Future
      :param callback: The callback function to register with the Future.
      :type callback: func
      :param errback: The errorback function to register with the Future.
      :type errback: func
      """
      def done(f):
         try:
            res = f.result()
            callback(res)
         except Exception as e:
            errback(e)
      return future.add_done_callback(done)

   @staticmethod
   def gather_futures(futures, consume_exceptions=True):
      """
      Returns a future that gathers the results of a list of Futures.
      :param futures: The list of Futures to gather results from.
      :type future: list
      :param consume_exceptions: If True, exceptions in the tasks are treated the same as successful results, and gathered in the result list; otherwise, the first raised exception will be immediately propagated to the returned future.
      :type consume_exceptions: bool
      :returns: A Future fired with the result of all supplied Futures.
      :rtype: asyncio.Future
      """
      return asyncio.gather(*futures, return_exceptions=consume_exceptions)



class LoopMixin(FutureMixin, LogMixin):
   """
   A mixin that pulls in all loop-specific mixins for the asyncio loop.
   """
   pass
