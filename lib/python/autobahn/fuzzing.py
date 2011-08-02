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

from twisted.internet import reactor
from twisted.python import log
from websocket import WebSocketProtocol, WebSocketService, WebSocketServiceConnection, HttpException
from cases import Cases
import json
import binascii
import datetime
import random
import textwrap


def getUtcNow():
   now = datetime.datetime.utcnow()
   return now.strftime("%Y-%m-%dT%H:%M:%SZ")


class FuzzingServiceConnection(WebSocketServiceConnection):

   def connectionMade(self):
      WebSocketServiceConnection.connectionMade(self)
      self.case = None
      self.runCase = None
      self.caseAgent = None
      self.caseStarted = None
      self.wirelog = []


   def connectionLost(self, reason):
      WebSocketServiceConnection.connectionLost(self, reason)
      if self.runCase and self.caseStarted:
         caseResult = {"case": self.case,
                       "description": self.Case.DESCRIPTION,
                       "expectation": self.Case.EXPECTATION,
                       "agent": self.caseAgent,
                       "started": self.caseStarted,
                       "passed": self.runCase.passed,
                       "result": self.runCase.result,
                       "wirelog": self.wirelog,
                       "failedByMe": self.failedByMe}
         self.factory.logCase(caseResult)


   def logRxOctets(self, data):
      if self.runCase:
         self.wirelog.append(("RO", binascii.b2a_hex(data)))
      else:
         WebSocketServiceConnection.logRxOctets(self, data)


   def logTxOctets(self, data, sync):
      if self.runCase:
         self.wirelog.append(("TO", binascii.b2a_hex(data), sync))
      else:
         WebSocketServiceConnection.logTxOctets(self, data, sync)


   def logRxFrame(self, fin, rsv, opcode, masked, payload_len, mask, payload):
      if self.runCase:
         self.wirelog.append(("RF", payload, opcode, fin, rsv, masked, mask))
      else:
         WebSocketServiceConnection.logRxFrame(self, fin, rsv, opcode, masked, payload_len, mask, payload)


   def logTxFrame(self, opcode, payload, fin, rsv, mask, payload_len, chopsize, sync):
      if self.runCase:
         self.wirelog.append(("TF", payload, opcode, fin, rsv, mask, payload_len, chopsize, sync))
      else:
         WebSocketServiceConnection.logTxFrame(self, opcode, payload, fin, rsv, mask, payload_len, chopsize, sync)


   def continueLater(self, delay, fun):
      self.wirelog.append(("CT", delay))
      reactor.callLater(delay, fun)


   def killAfter(self, delay):
      self.wirelog.append(("KL", delay))
      reactor.callLater(delay, self.failConnection)


   def onConnect(self, host, path, params, origin, protocols):
      if self.debug:
         log.msg("connection received from %s for host %s, path %s, parms %s, origin %s, protocols %s" % (self.peerstr, host, path, str(params), origin, str(protocols)))

      if params.has_key("agent"):
         if len(params["agent"]) > 1:
            raise Exception("multiple agents specified")
         self.caseAgent = params["agent"][0]

      if params.has_key("case"):
         if len(params["case"]) > 1:
            raise Exception("multiple test cases specified")
         try:
            self.case = int(params["case"][0])
         except:
            raise Exception("invalid test case ID %s" % params["case"][0])

      if self.case:
         if self.case >= 1 and self.case <= len(Cases):
            self.Case = Cases[self.case - 1]
            self.runCase = self.Case(self)
         else:
            raise Exception("case %s not found" % self.case)

      if path == "/runcase":
         if not self.runCase:
            raise Exception("need case to run")
         if not self.caseAgent:
            raise Exception("need agent to run case")
         self.caseStarted = getUtcNow()

      return None


   def onOpen(self):
      if self.runCase:
         self.runCase.onOpen()


   def onPong(self, payload):
      if self.runCase:
         self.runCase.onPong(payload)
      else:
         if self.debug:
            log.msg("Pong received: " + payload)


   def onMessage(self, msg, binary):

      if self.runCase:
         self.runCase.onMessage(msg, binary)

      else:

         if binary:

            raise Exception("binary command message")

         else:

            try:
               obj = json.loads(msg)
            except:
               raise Exception("could not parse command")

            ## send one frame as specified
            ##
            if obj[0] == "sendframe":
               pl = obj[1].get("payload", "")
               self.sendFrame(opcode = obj[1]["opcode"],
                              payload = pl.encode("UTF-8"),
                              fin = obj[1].get("fin", True),
                              rsv = obj[1].get("rsv", 0),
                              mask = obj[1].get("mask", None),
                              payload_len = obj[1].get("payload_len", None),
                              chopsize = obj[1].get("chopsize", None),
                              sync = obj[1].get("sync", False))

            ## send multiple frames as specified
            ##
            elif obj[0] == "sendframes":
               frames = obj[1]
               for frame in frames:
                  pl = frame.get("payload", "")
                  self.sendFrame(opcode = frame["opcode"],
                                 payload = pl.encode("UTF-8"),
                                 fin = frame.get("fin", True),
                                 rsv = frame.get("rsv", 0),
                                 mask = frame.get("mask", None),
                                 payload_len = frame.get("payload_len", None),
                                 chopsize = frame.get("chopsize", None),
                                 sync = frame.get("sync", False))

            ## send close
            ##
            elif obj[0] == "close":
               spec = obj[1]
               self.sendClose(spec.get("code", None), spec.get("reason", None))

            ## echo argument
            ##
            elif obj[0] == "echo":
               spec = obj[1]
               self.sendFrame(opcode = 1, payload = spec.get("payload", ""), payload_len = spec.get("payload_len", None))

            else:
               raise Exception("fuzzing server received unknown command" % obj[0])


class FuzzingService(WebSocketService):

   protocol = FuzzingServiceConnection

   css = """
<style lang="css">
   body {
    background-color: #F4F4F4;
    color: #333;
    font-family: Segoe UI,Tahoma,Arial,Verdana,sans-serif;
   }

   pre.wirelog_rx_octets {color: #aaa; margin: 0; background-color: #060; padding: 2px;}
   pre.wirelog_tx_octets {color: #aaa; margin: 0; background-color: #600; padding: 2px;}
   pre.wirelog_tx_octets_sync {color: #aaa; margin: 0; background-color: #606; padding: 2px;}

   pre.wirelog_rx_frame {color: #fff; margin: 0; background-color: #0a0; padding: 2px;}
   pre.wirelog_tx_frame {color: #fff; margin: 0; background-color: #a00; padding: 2px;}
   pre.wirelog_tx_frame_sync {color: #fff; margin: 0; background-color: #a0a; padding: 2px;}

   pre.wirelog_delay {color: #fff; margin: 0; background-color: #000; padding: 2px;}
   pre.wirelog_kill_after {color: #fff; margin: 0; background-color: #000; padding: 2px;}

   pre.wirelog_tcp_closed_by_server {color: #fff; margin: 0; background-color: #008; padding: 2px;}
   pre.wirelog_tcp_closed_by_client {color: #fff; margin: 0; background-color: #000; padding: 2px;}
</style>
"""

   def __init__(self, debug = False):
      self.debug = debug
      self.agents = {}


   def startFactory(self):
      pass


   def stopFactory(self):
      pass


   def logCase(self, caseResults):
      agent = caseResults["agent"]
      case = caseResults["case"]
      if not self.agents.has_key(agent):
         self.agents[agent] = {}
      self.agents[agent][case] = caseResults


   def getCase(self, agent, case):
      return self.agents[agent][case]


   def saveReport(self, reportFile):
      f = reportFile
      f.write("<html><body><head>%s</head>\n" % FuzzingService.css)
      for agent in self.agents:
         f.write("<h1>%s</h1>\n" % agent)

         cases = self.agents[agent]

         for c in cases:

            case = cases[c]

            f.write('<h2 class="case_heading">Case %d</h2>' % case["case"])

            f.write('<p class="case_result">Description: %s</p>' % case["description"])
            f.write('<p class="case_result">Expectation: %s</p>' % case["expectation"])

            f.write('<p class="case_passed">Passed: %s</p>' % case["passed"])
            f.write('<p class="case_result">Result: %s</p>' % case["result"])

            ## write out wire log
            ##
            f.write('<p class="wirelog">')
            wl = case["wirelog"]
            i = 0
            for t in wl:

               if t[0] == "RO":
                  prefix = "RX OCTETS"
                  css_class = "wirelog_rx_octets"

               elif t[0] == "TO":
                  prefix = "TX OCTETS"
                  if t[2]:
                     css_class = "wirelog_tx_octets_sync"
                  else:
                     css_class = "wirelog_tx_octets"

               elif t[0] == "RF":
                  prefix = "RX FRAME "
                  css_class = "wirelog_rx_frame"

               elif t[0] == "TF":
                  prefix = "TX FRAME "
                  if t[8] or t[7] is not None:
                     css_class = "wirelog_tx_frame_sync"
                  else:
                     css_class = "wirelog_tx_frame"

               elif t[0] in ["CT", "KL"]:
                  pass

               else:
                  raise Exception("logic error")

               if t[0] in ["RO", "TO", "RF", "TF"]:

                  lines = textwrap.wrap(t[1], 100)
                  if t[0] in ["RO", "TO"]:
                     if len(lines) > 0:
                        f.write('<pre class="%s">%03d %s: %s</pre>' % (css_class, i, prefix, lines[0]))
                        for ll in lines[1:]:
                           f.write('<pre class="%s">%s%s</pre>' % (css_class, (2+4+len(prefix))*" ", ll))
                  else:
                     if t[0] == "RF":
                        if t[6]:
                           mmask = binascii.b2a_hex(t[6])
                        else:
                           mmask = str(t[6])
                        f.write('<pre class="%s">%03d %s: OPCODE=%s, FIN=%s, RSV=%s, MASKED=%s, MASK=%s</pre>' % (css_class, i, prefix, str(t[2]), str(t[3]), str(t[4]), str(t[5]), mmask))
                     elif t[0] == "TF":
                        f.write('<pre class="%s">%03d %s: OPCODE=%s, FIN=%s, RSV=%s, MASK=%s, PAYLOAD-REPEAT-LEN=%s, CHOPSIZE=%s, SYNC=%s</pre>' % (css_class, i, prefix, str(t[2]), str(t[3]), str(t[4]), str(t[5]), str(t[6]), str(t[7]), str(t[8])))
                     else:
                        raise Exception("logic error")
                     for ll in lines:
                        f.write('<pre class="%s">%s%s</pre>' % (css_class, (2+4+len(prefix))*" ", ll))

               elif t[0] == "CT":
                  f.write('<pre class="wirelog_delay">%03d DELAY %f sec</pre>' % (i, t[1]))

               elif t[0] == "KL":
                  f.write('<pre class="wirelog_kill_after">%03d KILL AFTER %f sec</pre>' % (i, t[1]))

               else:
                  raise Exception("logic error")

               i += 1

            if case["failedByMe"]:
               f.write('<pre class="wirelog_tcp_closed_by_server">%03d TCP CLOSED BY SERVER</pre>' % i)
            else:
               f.write('<pre class="wirelog_tcp_closed_by_client">%03d TCP CLOSED BY CLIENT</pre>' % i)
            f.write('</p>')

      f.write("</body></html>\n")
