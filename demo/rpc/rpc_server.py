###############################################################################
##
##  Copyright 2011 Tavendo GmbH
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

import sys
from twisted.internet import reactor, defer
from twisted.python import log
from autobahn.autobahn import rpc, AutobahnServerFactory, AutobahnServerProtocol


class RpcServerProtocol(AutobahnServerProtocol):

   pass



class RpcServerFactory(AutobahnServerFactory):

   protocol = RpcServerProtocol

   def __init__(self, debug):
      AutobahnServerFactory.__init__(self, debug)
      #self.registerProcedure("sum", self.sum)
      #self.registerProcedure("asyncSum", self.asyncSum)
      #self.registerProcedure("square", self.square)

   @rpc("sum")
   def sum(self, arg):
      return reduce(lambda x, y: x + y, arg)

   @rpc
   def asyncSum(self, arg):
      print "asyncSum", arg
      d = defer.Deferred()
      reactor.callLater(3, d.callback, self.sum(arg))
      return d

   @rpc
   def square(self, arg):
      return arg * arg


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = RpcServerFactory(debug = False)
   reactor.listenTCP(9000, factory)
   reactor.run()
