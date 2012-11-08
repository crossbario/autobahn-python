###############################################################################
##
##  Copyright 2012 Tavendo GmbH
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


import twisted
from twisted.python import log, usage
from twisted.application.service import MultiService

from echoservice import EchoService


class AppService(MultiService):
   """
   Our application service hierarchy.
   """

   def startService(self):

      ## create WebSocket echo service and make it a child of our app service
      svc = EchoService(self.port, self.debug)
      svc.setName("EchoService")
      svc.setServiceParent(self)

      MultiService.startService(self)



class Options(usage.Options):
   optFlags = [['debug', 'd', 'Emit debug messages']]
   optParameters = [["port", "p", 8080, "Listening port (for both Web and WebSocket) - default 8080."]]



def makeService(options):
   """
   This will be called from twistd plugin system and we are supposed to
   create and return our application service.
   """

   ## create application service and forward command line options ..
   service = AppService()
   service.port = int(options['port'])
   service.debug = options['debug']

   return service
