###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from __future__ import absolute_import

__all = (
   'sleep',
)

from twisted.internet.defer import Deferred, DeferredList, maybeDeferred
from twisted.internet.address import IPv4Address, IPv6Address, UNIXAddress


def sleep(delay, reactor = None):
   """
   Inline sleep for use in coroutines (Twisted ``inlineCallback`` decorated functions).

   .. seealso::
      * `twisted.internet.defer.inlineCallbacks <http://twistedmatrix.com/documents/current/api/twisted.internet.defer.html#inlineCallbacks>`__
      * `twisted.internet.interfaces.IReactorTime <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IReactorTime.html>`__

   :param delay: Time to sleep in seconds.
   :type delay: float
   :param reactor: The Twisted reactor to use.
   :type reactor: None or provider of ``IReactorTime``.
   """
   if not reactor:
      from twisted.internet import reactor
   d = Deferred()
   reactor.callLater(delay, d.callback, None)
   return d


def peer2str(addr):
   """
   Convert a Twisted address, as returned from ``self.transport.getPeer()`` to a string
   """
   if isinstance(addr, IPv4Address):
      res = "tcp4:{0}:{1}".format(addr.host, addr.port)
   elif isinstance(addr, IPv6Address):
      res = "tcp6:{0}:{1}".format(addr.host, addr.port)
   elif isinstance(addr, UNIXAddress):
      res = "unix:{0}".format(addr.name)
   else:
      # gracefully fallback if we can't map the peer's address
      res = "?:{0}".format(addr)

   return res



class FutureMixin:
   """
   Mixin for Twisted style Futures ("Deferreds").
   """

   @staticmethod
   def create_future():
      """"
      Creates a new twisted Deferred
      """
      return Deferred()

   @staticmethod
   def as_future(fun, *args, **kwargs):
      """
      Executes a function with the given arguments
      and wraps the result into a Deferred.
      :param fun: The function to be called.
      :type fun: func
      :param args: The argument list for the supplied function.
      :type args: list
      :param kwargs: The keyword argument dict for the supplied function.
      :type kwargs: dict
      :return: The functions result wrapped in a Deferred
      :rtype: twisted.internet.defer.Deferred
      """
      return maybeDeferred(fun, *args, **kwargs)

   @staticmethod
   def resolve_future(deferred, value):
      """
      Resolve a Deferred sucessfully with a given value.
      :param deferred: The Deferred to be resolved.
      :type deferred: twisted.internet.defer.Deferred
      :param value: The value to resolve the Deferred with.
      :type value: any
      """
      deferred.callback(value)

   @staticmethod
   def reject_future(deferred, value):
      """
      Rejects a Deferred with a given exception.
      :param deferred: The Deferred to be rejected.
      :type deferred: twisted.internet.defer.Deferred
      :param exception: The exception to reject the Deferred with.
      :type exception: Exception
      """
      deferred.errback(value)

   @staticmethod
   def add_future_callbacks(deferred, callback, errback):
      """
      Register callback and errback functions with a Deferred.
      :param deferred: The Deferred to register callbacks with.
      :type deferred: twisted.internet.defer.Deferred
      :param callback: The callback function to register with the Deferred.
      :type callback: func
      :param errback: The errback function to register with the Deferred.
      :type errback: func
      """
      return deferred.addCallbacks(callback, errback)

   @staticmethod
   def gather_futures(deferreds, consume_exceptions=True):
      """
      Returns a DeferredList that gathers the results of a list of Deferreds.
      :param deferreds: The list of Deferreds to gather results from.
      :type deferreds: list
      :param consume_exceptions: If True, exceptions in the tasks are treated the same as successful results, and gathered in the result list; otherwise, the first raised exception will be immediately propagated to the returned future.
      :type consume_exceptions: bool
      :returns: A DeferredList fired with the result of all supplied Deferreds.
      :rtype: twisted.internet.defer.DeferredList
      """
      return DeferredList(deferreds, consumeErrors=consume_exceptions)



class LoopMixin(FutureMixin):
    """
    A mixin that pulls in all loop-specific mixins for the twisted loop.
    """
    pass
