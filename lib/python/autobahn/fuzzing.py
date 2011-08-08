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
from websocket import WebSocketProtocol, WebSocketServerFactory, WebSocketServerProtocol, HttpException
from case import Case, Cases, CaseCategories, CaseSubCategories, caseClasstoId, caseClasstoIdTuple
import json
import binascii
import datetime
import time
import random
import textwrap
import os


def getUtcNow():
   now = datetime.datetime.utcnow()
   return now.strftime("%Y-%m-%dT%H:%M:%SZ")


class FuzzingServerProtocol(WebSocketServerProtocol):

   MAX_WIRE_LOG_DATA = 256


   def connectionMade(self):
      WebSocketServerProtocol.connectionMade(self)
      self.case = None
      self.runCase = None
      self.caseAgent = None
      self.caseStarted = None
      self.caseStart = 0
      self.caseEnd = 0
      self.wirelog = []
      self.createWirelog = True


   def connectionLost(self, reason):

      WebSocketServerProtocol.connectionLost(self, reason)

      if self.runCase:

         self.runCase.onConnectionLost(self.failedByMe)
         self.caseEnd = time.time()

         caseResult = {"case": self.case,
                       "id": caseClasstoId(self.Case),
                       "description": self.Case.DESCRIPTION,
                       "expectation": self.Case.EXPECTATION,
                       "agent": self.caseAgent,
                       "started": self.caseStarted,
                       "duration": int(round(1000. * (self.caseEnd - self.caseStart))), # case execution time in ms
                       "reportTime": self.runCase.reportTime, # True/False switch to control report output of duration
                       "behavior": self.runCase.behavior,
                       "expected": self.runCase.expected,
                       "received": self.runCase.received,
                       "result": self.runCase.result,
                       "wirelog": self.wirelog,
                       "createWirelog": self.createWirelog,
                       "failedByMe": self.failedByMe}

         self.factory.logCase(caseResult)


   def binLogData(self, data):
      if len(data) > FuzzingServerProtocol.MAX_WIRE_LOG_DATA:
         dd = binascii.b2a_hex(data[:FuzzingServerProtocol.MAX_WIRE_LOG_DATA]) + " ..."
      else:
         dd = binascii.b2a_hex(data)
      return dd


   def asciiLogData(self, data):
      if len(data) > FuzzingServerProtocol.MAX_WIRE_LOG_DATA:
         dd = data[:FuzzingServerProtocol.MAX_WIRE_LOG_DATA] + " ..."
      else:
         dd = data
      return dd


   def logRxOctets(self, data):
      if self.createWirelog:
         self.wirelog.append(("RO", self.binLogData(data)))
      else:
         WebSocketServerProtocol.logRxOctets(self, data)


   def logTxOctets(self, data, sync):
      if self.createWirelog:
         self.wirelog.append(("TO", self.binLogData(data), sync))
      else:
         WebSocketServerProtocol.logTxOctets(self, data, sync)


   def logRxFrame(self, fin, rsv, opcode, masked, payload_len, mask, payload):
      if self.createWirelog:
         self.wirelog.append(("RF", self.asciiLogData(payload), opcode, fin, rsv, masked, mask))
      else:
         WebSocketServerProtocol.logRxFrame(self, fin, rsv, opcode, masked, payload_len, mask, payload)


   def logTxFrame(self, opcode, payload, fin, rsv, mask, payload_len, chopsize, sync):
      if self.createWirelog:
         self.wirelog.append(("TF", self.asciiLogData(payload), opcode, fin, rsv, mask, payload_len, chopsize, sync))
      else:
         WebSocketServerProtocol.logTxFrame(self, opcode, payload, fin, rsv, mask, payload_len, chopsize, sync)


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

      if path == "/runCase":
         if not self.runCase:
            raise Exception("need case to run")
         if not self.caseAgent:
            raise Exception("need agent to run case")
         self.caseStarted = getUtcNow()
         print "Running test case ID %s for user agent %s for peer %s" % (caseClasstoId(self.Case), self.caseAgent, self.peerstr)

      elif path == "/updateReports":
         if not self.caseAgent:
            raise Exception("need agent to update reports for")
         print "Updating reports, requested by peer %s" % self.peerstr

      elif path == "/getCaseCount":
         pass

      else:
         print "Entering direct command mode for peer %s" % self.peerstr

      self.path = path

      return None


   def onOpen(self):

      if self.runCase:

         cc = caseClasstoIdTuple(self.runCase.__class__)

         ## FF7 crashes on these
         ##
         if self.caseAgent.find("Firefox/7") >= 0 and cc[0:2] == (9, 3):
            print "Skipping fragmented message test case for broken FF/7 !!!"
            self.runCase = None
            self.sendClose()
            return

         ## FF and Chrome dont yet implement binary messages
         ##
         if (self.caseAgent.find("Firefox") >= 0 or self.caseAgent.find("Chrome") >= 0) and cc[0:2] in [(1, 2), (9, 2), (9, 4), (9,6)]:
            print "Skipping binary message test case for browser client !!!"
            self.runCase = None
            self.sendClose()
            return

         self.caseStart = time.time()
         self.runCase.onOpen()

      elif self.path == "/updateReports":
         self.factory.createReports()
         self.sendClose()

      elif self.path == "/getCaseCount":
         self.sendMessage(json.dumps(len(Cases)))
         self.sendClose()

      else:
         pass


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


class FuzzingServerFactory(WebSocketServerFactory):

   protocol = FuzzingServerProtocol

   ## CSS common for all reports
   ##
   css_common = """
      body
      {
         background-color: #F4F4F4;
         color: #333;
         font-family: Segoe UI,Tahoma,Arial,Verdana,sans-serif;
      }

      p#intro
      {
         margin-left: 30px;
         font-size: 1.2em;
      }

      p#case_desc
      {
         border-radius: 10px;
         background-color: #eee;
         padding: 20px;
         margin: 20px;
      }

      p#case_expect
      {
         border-radius: 10px;
         background-color: #eee;
         padding: 20px;
         margin: 20px;
      }

      p#case_result
      {
         border-radius: 10px;
         background-color: #eee;
         padding: 20px;
         margin: 20px;
      }

      h1
      {
      }

      h2
      {
         margin-top: 60px;
         margin-left: 30px;
      }

      h3
      {
         margin-left: 50px;
      }
   """

   ## CSS for Master report
   ##
   css_master = """
      table
      {
         border-collapse: collapse;
         border-spacing: 0px;
         margin-left: 40px;
         margin-bottom: 40px;
         margin-top: 20px;
      }

      td
      {
         margin: 0;
         border: 1px #fff solid;
         padding-top: 6px;
         padding-bottom: 6px;
         padding-left: 16px;
         padding-right: 16px;
      }

      tr#agent_case_result_row a
      {
         color: #eee;
      }

      td#agent
      {
         color: #fff;
         font-size: 1.0em;
         min-width: 140px;
         text-align: center;
         background-color: #048;
      }

      td#case_category
      {
         min-width: 180px;
         color: #fff;
         background-color: #000;
         text-align: left;
         padding-left: 20px;
         font-size: 1.0em;
      }

      td#case_subcategory
      {
         color: #fff;
         background-color: #333;
         text-align: left;
         padding-left: 30px;
         font-size: 0.9em;
      }

      td#case
      {
         background-color: #666;
         text-align: left;
         padding-left: 40px;
         font-size: 0.9em;
      }

      span#case_duration
      {
         font-size: 0.7em;
         color: #fff;
      }

      td#case_ok
      {
         background-color: #0a0;
         text-align: center;
      }

      td#case_non_strict
      {
         background-color: #aa0;
         text-align: center;
      }

      td#case_failed
      {
         background-color: #900;
         text-align: center;
      }

      td#case_missing
      {
         color: #fff;
         background-color: #a05a2c;
         text-align: center;
      }
   """

   ## CSS for Agent/Case detail report
   ##
   css_detail = """
      h2
      {
         margin-top: 30px;
      }

      p#case_ok
      {
         color: #fff;
         border-radius: 10px;
         background-color: #0a0;
         padding: 20px;
         margin: 20px;
         font-size: 1.2em;
      }

      p#case_non_strict
      {
         color: #fff;
         border-radius: 10px;
         background-color: #990;
         padding: 20px;
         margin: 20px;
         font-size: 1.2em;
      }

      p#case_failed
      {
         color: #fff;
         border-radius: 10px;
         background-color: #900;
         padding: 20px;
         margin: 20px;
         font-size: 1.2em;
      }

      div#wirelog
      {
         margin-top: 20px;
         margin-bottom: 80px;
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
   """


   def __init__(self, debug = False, outdir = "reports"):
      self.debug = debug
      self.outdir = outdir
      self.agents = {}
      self.cases = {}


   def startFactory(self):
      pass


   def stopFactory(self):
      pass


   def logCase(self, caseResults):

      agent = caseResults["agent"]
      case = caseResults["case"]

      ## index by agent->case
      ##
      if not self.agents.has_key(agent):
         self.agents[agent] = {}
      self.agents[agent][case] = caseResults

      ## index by case->agent
      ##
      if not self.cases.has_key(case):
         self.cases[case] = {}
      self.cases[case][agent] = caseResults


   def getCase(self, agent, case):
      return self.agents[agent][case]


   def createReports(self):

      if not os.path.exists(self.outdir):
         os.makedirs(self.outdir)

      self.createMasterReport(self.outdir)

      for agentId in self.agents:
         for caseNo in self.agents[agentId]:
            self.createAgentCaseReport(agentId, caseNo, self.outdir)


   def cleanForFilename(self, str):
      s0 = ''.join([c if c in "abcdefghjiklmnopqrstuvwxyz0123456789" else " " for c in str.strip().lower()])
      s1 = s0.strip()
      s2 = s1.replace(' ', '_')
      return s2


   def makeAgentCaseReportFilename(self, agentId, caseNo):
      c = (caseClasstoId(Cases[caseNo - 1])).replace('.', '_')
      return self.cleanForFilename(agentId) + "_case_" + c + ".html"


   def createMasterReport(self, outdir):

      report_filename = "index.html"
      f = open(os.path.join(outdir, report_filename), 'w')

      f.write('<html><body><head><style lang="css">%s %s</style></head>' % (FuzzingServerFactory.css_common, FuzzingServerFactory.css_master))

      f.write('<h1>WebSockets Protocol Test Report</h1>')

      f.write('<p id="intro">Test summary report generated on</p>')
      f.write('<p id="intro" style="margin-left: 80px;"><i>%s</i></p>' % getUtcNow())
      f.write('<p id="intro">by <a href="%s">Autobahn</a> WebSockets.</p>' % "http://www.tavendo.de/autobahn")

      f.write('<h2>Test Results</h2>')

      f.write('<table id="agent_case_results">')

      ## sorted list of agents for which test cases where run
      ##
      agentList = sorted(self.agents.keys())

      ## create list of case indexes order by case ID
      ##
      cl = []
      i = 1
      for c in Cases:
         cl.append((caseClasstoIdTuple(c) , i))
         i += 1
      cl = sorted(cl)
      caseList = []
      for c in cl:
         caseList.append(c[1])

      lastCaseCategory = None
      lastCaseSubCategory = None

      for caseNo in caseList:

         ## Case ID and category
         ##
         caseId = caseClasstoId(Cases[caseNo - 1])
         caseCategoryIndex = caseId.split('.')[0]
         caseCategory = CaseCategories.get(caseCategoryIndex, "Misc")
         caseSubCategoryIndex = '.'.join(caseId.split('.')[:2])
         caseSubCategory = CaseSubCategories.get(caseSubCategoryIndex, None)

         ## Category row
         ##
         if caseCategory != lastCaseCategory:
            f.write('<tr id="case_category_row">')
            f.write('<td id="case_category">%s %s</td>' % (caseCategoryIndex, caseCategory))
            for agentId in agentList:
               f.write('<td id="agent">%s</td>' % agentId)
            f.write('</tr>')
            lastCaseCategory = caseCategory
            lastCaseSubCategory = None

         if caseSubCategory != lastCaseSubCategory:
            f.write('<tr id="case_subcategory_row">')
            f.write('<td id="case_subcategory" colspan="%d">%s %s</td>' % (len(agentList) + 1, caseSubCategoryIndex, caseSubCategory))
            lastCaseSubCategory = caseSubCategory

         f.write('<tr id="agent_case_result_row">')
         f.write('<td id="case"><a href="#case_desc_%d">Case %s</a></td>' % (caseNo, caseId))

         ## Agent/Case Result
         ##
         for agentId in agentList:
            if self.agents[agentId].has_key(caseNo):

               case = self.agents[agentId][caseNo]

               agent_case_report_file = self.makeAgentCaseReportFilename(agentId, caseNo)

               if case["behavior"] == Case.OK:
                  td_text = "Pass"
                  td_class = "case_ok"
               elif case["behavior"] == Case.NON_STRICT:
                  td_text = "Non-Strict"
                  td_class = "case_non_strict"
               else:
                  td_text = "Fail"
                  td_class = "case_failed"

               if case["reportTime"]:
                  f.write('<td id="%s"><a href="%s">%s</a><br/><span id="case_duration">%s ms</span></td>' % (td_class, agent_case_report_file, td_text, case["duration"]))
               else:
                  f.write('<td id="%s"><a href="%s">%s</a></td>' % (td_class, agent_case_report_file, td_text))

            else:
               f.write('<td id="case_missing">Missing</td>')

         f.write("</tr>")

      f.write("</table>")

      f.write('<h2>Test Cases</h2>')

      for caseNo in caseList:

         CCase = Cases[caseNo - 1]

         f.write('<a name="case_desc_%d"></a>' % caseNo)
         f.write('<h3 id="case_desc_title">Case %s</h2>' % caseClasstoId(CCase))
         f.write('<p id="case_desc"><i>Description</i><br/><br/> %s</p>' % CCase.DESCRIPTION)
         f.write('<p id="case_expect"><i>Expectation</i><br/><br/> %s</p>' % CCase.EXPECTATION)

      f.write("</body></html>")

      f.close()
      return report_filename


   def createAgentCaseReport(self, agentId, caseNo, outdir):

      if not self.agents.has_key(agentId):
         raise Exception("no test data stored for agent %s" % agentId)

      if not self.agents[agentId].has_key(caseNo):
         raise Exception("no test data stored for case %s with agent %s" % (caseNo, agentId))

      case = self.agents[agentId][caseNo]

      report_filename = self.makeAgentCaseReportFilename(agentId, caseNo)

      f = open(os.path.join(outdir, report_filename), 'w')

      f.write('<html><body><head><style lang="css">%s %s</style></head>' % (FuzzingServerFactory.css_common, FuzzingServerFactory.css_detail))

      f.write('<h1>%s - Test Case %s</h1>' % (case["agent"], case["id"]))

      if case["behavior"] == Case.OK:
         f.write('<p id="case_ok"><b>Pass</b> (%s - %d ms)</p>' % (case["started"], case["duration"]))
      elif case["behavior"] ==  Case.NON_STRICT:
         f.write('<p id="case_non_strict"><b>Non-Strict</b> (%s - %d ms)</p>' % (case["started"], case["duration"]))
      else:
         f.write('<p id="case_failed"><b>Fail</b> (%s - %d ms)</p>' % (case["started"], case["duration"]))

      f.write('<h2>Case</h2>')
      f.write('<p id="case_desc"><i>Description</i><br/><br/>%s</p>' % case["description"])
      f.write('<p id="case_expect"><i>Expectation</i><br/><br/>%s</p>' % case["expectation"])

      f.write('<h2>Result</h2>')

      if case["result"] and case["result"] != "":
         f.write('<p id="case_result">%s</p>' % case["result"])

      if case["expected"] and case["received"]:
         es = str(case["expected"])
         if len(es) > 400:
            es = es[:400] + " ..."
         f.write('<p id="case_result">Expected = %s</p>' % es)

         rs = str(case["received"])
         if len(rs) > 400:
            rs = rs[:400] + " ..."
         f.write('<p id="case_result">Actual = %s</p>' % rs)

      f.write('<h2>Wire Log</h2>')

      if not case["createWirelog"]:
         f.write('<p style="margin-left: 40px; color: #f00;"><i>Wire log after handshake disabled!</i></p>')

      ## write out wire log
      ##
      f.write('<div id="wirelog">')
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
      f.write('</div>')

      f.write("</body></html>")

      f.close()
      return report_filename
