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

import time

from twisted.internet import reactor
from twisted.internet.defer import DeferredList 

from autobahn.twisted.wamp import ApplicationSession



class Component(ApplicationSession):
   """
   An application component using the time service.
   """

   def onConnect(self):
      self.join("realm1")


   def onJoin(self, details):

      def got(res, started, msg):
         duration = 1000. * (time.clock() - started)
         print("{}: {} in {}".format(msg, res, duration))

      t1 = time.clock()
      d1 = self.call('com.math.slowsquare', 3)
      d1.addCallback(got, t1, "Slow Square")

      t2 = time.clock()
      d2 = self.call('com.math.square', 3)
      d2.addCallback(got, t2, "Quick Square")

      def done(_):
         print("All finished.")
         self.leave()

      DeferredList ([d1, d2]).addBoth(done)


   def onLeave(self, details):
      self.disconnect()


   def onDisconnect(self):
      reactor.stop()
