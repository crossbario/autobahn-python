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

from twisted.internet.defer import Deferred
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
