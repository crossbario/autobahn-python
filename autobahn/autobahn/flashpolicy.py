###############################################################################
##
##  Copyright 2013 Tavendo GmbH
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

import re

from twisted.python import log
from twisted.internet import reactor
from twisted.application.internet import TCPServer
from twisted.internet.protocol import Protocol, Factory


class FlashPolicyProtocol(Protocol):
   """
   Flash Player 9 (version 9.0.124.0 and above) implements a strict new access
   policy for Flash applications that make Socket or XMLSocket connections to
   a remote host. It now requires the presence of a socket policy file
   on the server.

   http://www.lightsphere.com/dev/articles/flash_socket_policy.html

   We want this to support the Flash WebSockets bridge which is needed for
   older browser, in particular MSIE9/8.
   """

   REQUESTPAT = re.compile("^\s*<policy-file-request\s*/>")
   REQUESTMAXLEN = 200
   REQUESTTIMEOUT = 5
   POLICYFILE = """<?xml version="1.0"?><cross-domain-policy><allow-access-from domain="*" to-ports="%d" /></cross-domain-policy>"""

   def __init__(self, allowedPort):
      self.allowedPort = allowedPort
      self.received = ""
      self.dropConnection = None


   def connectionMade(self):
      ## DoS protection
      ##
      def dropConnection():
         self.transport.abortConnection()
         self.dropConnection = None
      self.dropConnection = reactor.callLater(FlashPolicyProtocol.REQUESTTIMEOUT, dropConnection)


   def connectionLost(self, reason):
      if self.dropConnection:
         self.dropConnection.cancel()
         self.dropConnection = None


   def dataReceived(self, data):
      self.received += data
      if FlashPolicyProtocol.REQUESTPAT.match(self.received):
         ## got valid request: send policy file
         ##
         self.transport.write(FlashPolicyProtocol.POLICYFILE % self.allowedPort)
         self.transport.loseConnection()
      elif len(self.received) > FlashPolicyProtocol.REQUESTMAXLEN:
         ## possible DoS attack
         ##
         self.transport.abortConnection()
      else:
         ## need more data
         ##
         pass


class FlashPolicyFactory(Factory):

   def __init__(self, allowedPort):
      self.allowedPort = allowedPort

   def buildProtocol(self, addr):
      return FlashPolicyProtocol(self.allowedPort)
