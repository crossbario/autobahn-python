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

import json
import binascii
import datetime
import time
import random
import textwrap
import os
import re
from twisted.internet import reactor
from twisted.python import log
import autobahn
from websocket import WebSocketProtocol, WebSocketServerFactory, WebSocketServerProtocol,  WebSocketClientFactory, WebSocketClientProtocol, HttpException
from websocket import connectWS, listenWS
from case import Case, Cases, CaseCategories, CaseSubCategories, caseClasstoId, caseClasstoIdTuple, CasesIndices, CasesById, caseIdtoIdTuple, caseIdTupletoId
from util import utcnow
from report import CSS_COMMON, CSS_DETAIL_REPORT, CSS_MASTER_REPORT, JS_MASTER_REPORT


def resolveCasePatternList(patterns):
   """
   Return list of test cases that match against a list of case patterns.
   """
   specCases = []
   for c in patterns:
      if c.find('*') >= 0:
         s = c.replace('.', '\.').replace('*', '.*')
         p = re.compile(s)
         t = []
         for x in CasesIndices.keys():
            if p.match(x):
               t.append(caseIdtoIdTuple(x))
         for h in sorted(t):
            specCases.append(caseIdTupletoId(h))
      else:
         specCases.append(c)
   return specCases


def parseSpecCases(spec):
   """
   Return list of test cases that match against case patterns, minus exclude patterns.
   """
   specCases = resolveCasePatternList(spec["cases"])
   if spec.has_key("exclude-cases"):
      excludeCases = resolveCasePatternList(spec["exclude-cases"])
   else:
      excludeCases = []
   c = list(set(specCases) - set(excludeCases))
   cases = [caseIdTupletoId(y) for y in sorted([caseIdtoIdTuple(x) for x in c])]
   return cases


class FuzzingProtocol:
   """
   Common mixin-base class for fuzzing server and client protocols.
   """

   MAX_WIRE_LOG_DATA = 256

   def connectionMade(self):

      self.case = None
      self.runCase = None
      self.caseAgent = None
      self.caseStarted = None
      self.caseStart = 0
      self.caseEnd = 0

      ## wire log
      ##
      self.createWirelog = True
      self.wirelog = []

      ## stats for octets and frames
      ##
      self.createStats = True
      self.rxOctetStats = {}
      self.rxFrameStats = {}
      self.txOctetStats = {}
      self.txFrameStats = {}


   def connectionLost(self, reason):
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
                       "behaviorClose": self.runCase.behaviorClose,
                       "expected": self.runCase.expected,
                       "expectedClose": self.runCase.expectedClose,
                       "received": self.runCase.received,
                       "result": self.runCase.result,
                       "resultClose": self.runCase.resultClose,
                       "wirelog": self.wirelog,
                       "createWirelog": self.createWirelog,
                       "closedByMe": self.closedByMe,
                       "failedByMe": self.failedByMe,
                       "droppedByMe": self.droppedByMe,
                       "wasClean": self.wasClean,
                       "wasNotCleanReason": self.wasNotCleanReason,
                       "wasServerConnectionDropTimeout": self.wasServerConnectionDropTimeout,
                       "wasCloseHandshakeTimeout": self.wasCloseHandshakeTimeout,
                       "localCloseCode": self.localCloseCode,
                       "localCloseReason": self.localCloseReason,
                       "remoteCloseCode": self.remoteCloseCode,
                       "remoteCloseReason": self.remoteCloseReason,
                       "isServer": self.isServer,
                       "createStats": self.createStats,
                       "rxOctetStats": self.rxOctetStats,
                       "rxFrameStats": self.rxFrameStats,
                       "txOctetStats": self.txOctetStats,
                       "txFrameStats": self.txFrameStats}
         self.factory.logCase(caseResult)
      # parent's connectionLost does useful things
      WebSocketProtocol.connectionLost(self,reason)


   def binLogData(self, data):
      if len(data) > FuzzingProtocol.MAX_WIRE_LOG_DATA:
         dd = binascii.b2a_hex(data[:FuzzingProtocol.MAX_WIRE_LOG_DATA]) + " ..."
      else:
         dd = binascii.b2a_hex(data)
      return dd


   def asciiLogData(self, data):
      if len(data) > FuzzingProtocol.MAX_WIRE_LOG_DATA:
         dd = data[:FuzzingProtocol.MAX_WIRE_LOG_DATA] + " ..."
      else:
         dd = data
      return dd


   def enableWirelog(self, enable):
      if enable != self.createWirelog:
         self.createWirelog = enable
         self.wirelog.append(("WLM", enable))


   def logRxOctets(self, data):
      if self.createStats:
         l = len(data)
         self.rxOctetStats[l] = self.rxOctetStats.get(l, 0) + 1
      if self.createWirelog:
         d = str(buffer(data))
         self.wirelog.append(("RO", self.binLogData(d)))
      else:
         WebSocketProtocol.logRxOctets(self, data)


   def logTxOctets(self, data, sync):
      if self.createStats:
         l = len(data)
         self.txOctetStats[l] = self.txOctetStats.get(l, 0) + 1
      if self.createWirelog:
         d = str(buffer(data))
         self.wirelog.append(("TO", self.binLogData(d), sync))
      else:
         WebSocketProtocol.logTxOctets(self, data, sync)


   def logRxFrame(self, fin, rsv, opcode, masked, payload_len, mask, payload):
      if self.createStats:
         self.rxFrameStats[opcode] = self.rxFrameStats.get(opcode, 0) + 1
      if self.createWirelog:
         d = str(buffer(payload))
         self.wirelog.append(("RF", self.asciiLogData(d), opcode, fin, rsv, masked, mask))
      else:
         WebSocketProtocol.logRxFrame(self, fin, rsv, opcode, masked, payload_len, mask, payload)


   def logTxFrame(self, opcode, payload, fin, rsv, mask, payload_len, chopsize, sync):
      if self.createStats:
         self.txFrameStats[opcode] = self.txFrameStats.get(opcode, 0) + 1
      if self.createWirelog:
         d = str(buffer(payload))
         self.wirelog.append(("TF", self.asciiLogData(d), opcode, fin, rsv, mask, payload_len, chopsize, sync))
      else:
         WebSocketProtocol.logTxFrame(self, opcode, payload, fin, rsv, mask, payload_len, chopsize, sync)


   def executeContinueLater(self, fun, tag):
      if self.state != WebSocketProtocol.STATE_CLOSED:
         self.wirelog.append(("CTE", tag))
         fun()
      else:
         pass # connection already gone


   def continueLater(self, delay, fun, tag = None):
      self.wirelog.append(("CT", delay, tag))
      reactor.callLater(delay, self.executeContinueLater, fun, tag)


   def executeKillAfter(self):
      if self.state != WebSocketProtocol.STATE_CLOSED:
         self.wirelog.append(("KLE", ))
         self.failConnection()
      else:
         pass # connection already gone


   def killAfter(self, delay):
      self.wirelog.append(("KL", delay))
      reactor.callLater(delay, self.executeKillAfter)


   def executeCloseAfter(self):
      if self.state != WebSocketProtocol.STATE_CLOSED:
         self.wirelog.append(("TIE", ))
         self.sendClose()
      else:
         pass # connection already gone


   def closeAfter(self, delay):
      self.wirelog.append(("TI", delay))
      reactor.callLater(delay, self.executeCloseAfter)


   def onOpen(self):

      if self.runCase:

         cc = caseClasstoIdTuple(self.runCase.__class__)

         ## IE10 crashes on these
         ##
         if self.caseAgent.find("MSIE") >= 0 and (cc[0:3] in [(6, 4, 3), (6, 4, 5)] or
                                                  cc[0:2] in [(2, 5)] or
                                                  cc[0:1][0] in [3, 4, 5]):
            print "Skipping test case for IE10 (crashes) !!!"
            self.runCase = None
            self.sendClose()
            return

         ## Chrome crashes on these
         ##
         if self.caseAgent.find("Chrome") >= 0 and cc[0:3] in [(6, 4, 3), (6, 4, 5)]:
            print "Skipping forever sending data after invalid UTF-8 for Chrome (crashes) !!!"
            self.runCase = None
            self.sendClose()
            return

         ## FF7 crashes on these
         ##
         if self.caseAgent.find("Firefox/7") >= 0 and cc[0:2] == (9, 3):
            print "Skipping fragmented message test case for Firefox/7 (crashes) !!!"
            self.runCase = None
            self.sendClose()
            return

         ## FF7 crashes on these
         ##
         if self.caseAgent.find("Firefox/7") >= 0 and cc[0:3] in [(6, 4, 2), (6, 4, 3), (6, 4, 4), (6, 4, 5)]:
            print "Skipping invalid UTF-8 test for Firefox/7 (crashes) !!!"
            self.runCase = None
            self.sendClose()
            return

         ## FF does not yet implement binary messages
         ##
         if self.caseAgent.find("Firefox") >= 0 and cc[0:2] in [(1, 2), (9, 2), (9, 4), (9, 6), (9, 8)]:
            print "Skipping binary message test case for Firefox !!!"
            self.runCase = None
            self.sendClose()
            return

         self.caseStart = time.time()
         self.runCase.onOpen()

      elif self.path == "/updateReports":
         self.factory.createReports()
         self.sendClose()

      elif self.path == "/getCaseCount":
         self.sendMessage(json.dumps(len(self.factory.specCases)))
         self.sendClose()

      else:
         pass


   def onPong(self, payload):
      if self.runCase:
         self.runCase.onPong(payload)
      else:
         if self.debug:
            log.msg("Pong received: " + payload)


   def onClose(self, wasClean, code, reason):
      if self.runCase:
         self.runCase.onClose(wasClean, code, reason)
      else:
         if self.debug:
            log.msg("Close received: " + code + " - " + reason)

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
               raise Exception("fuzzing peer received unknown command" % obj[0])


class FuzzingFactory:
   """
   Common mixin-base class for fuzzing server and client protocol factory.
   """

   MAX_CASE_PICKLE_LEN = 1000

   def __init__(self, debug = False, outdir = "reports"):
      self.repeatAgentRowPerSubcategory = True
      self.debug = debug
      self.outdir = outdir
      self.agents = {}
      self.cases = {}


   def logCase(self, caseResults):
      """
      Called from FuzzingProtocol instances when case has been finished to store case results.
      """

      agent = caseResults["agent"]
      case = caseResults["id"]

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


   def createReports(self):
      """
      Create reports from all data stored for test cases which have been executed.
      """

      ## create output directory when non-existent
      ##
      if not os.path.exists(self.outdir):
         os.makedirs(self.outdir)

      ## create master report
      ##
      self.createMasterReport(self.outdir)

      ## create case detail reports
      ##
      for agentId in self.agents:
         for caseId in self.agents[agentId]:
            self.createAgentCaseReport(agentId, caseId, self.outdir)


   def cleanForFilename(self, str):
      """
      Clean a string for use as filename.
      """
      s0 = ''.join([c if c in "abcdefghjiklmnopqrstuvwxyz0123456789" else " " for c in str.strip().lower()])
      s1 = s0.strip()
      s2 = s1.replace(' ', '_')
      return s2


   def makeAgentCaseReportFilename(self, agentId, caseId):
      """
      Create filename for case detail report from agent and case.
      """
      c = caseId.replace('.', '_')
      return self.cleanForFilename(agentId) + "_case_" + c + ".html"


   def limitString(self, s, limit, indicator = " ..."):
      ss = str(s)
      if len(ss) > limit - len(indicator):
         return ss[:limit - len(indicator)] + indicator
      else:
         return ss


   def createMasterReport(self, outdir):
      """
      Create report master HTML file.

      :param outdir: Directory where to create file.
      :type outdir: str
      :returns: str -- Name of created file.
      """

      ## open report file in create / write-truncate mode
      ##
      report_filename = "index.html"
      f = open(os.path.join(outdir, report_filename), 'w')

      ## write HTML
      ##
      f.write('<!DOCTYPE html>\n')
      f.write('<html>\n')
      f.write('   <head>\n')
      f.write('      <meta charset="utf-8" />\n')
      f.write('      <style lang="css">%s</style>\n' % CSS_COMMON)
      f.write('      <style lang="css">%s</style>\n' % CSS_MASTER_REPORT)
      f.write('      <script language="javascript">%s</script>\n' % JS_MASTER_REPORT % {"agents_cnt": len(self.agents.keys())})
      f.write('   </head>\n')
      f.write('   <body>\n')
      f.write('      <a href="#"><div id="toggle_button" class="unselectable" onclick="toggleClose();">Toggle Details</div></a>\n')
      f.write('      <a name="top"></a>\n')
      f.write('      <br/>\n')

      ## top logos
      f.write('      <center><img src="http://www.tavendo.de/static/autobahn/ws_protocol_test_report.png" border="0" width="820" height="46" alt="WebSockets Protocol Test Report"></img></a></center>\n')
      f.write('      <center><a href="http://www.tavendo.de/autobahn" title="Autobahn WebSockets"><img src="http://www.tavendo.de/static/autobahn/ws_protocol_test_report_autobahn.png" border="0" width="300" height="68" alt="Autobahn WebSockets"></img></a></center>\n')

      ## write report header
      ##
      f.write('      <div id="master_report_header" class="block">\n')
      f.write('         <p id="intro">Summary report generated on %s (UTC) by <a href="%s">Autobahn WebSockets</a> v%s.</p>\n' % (utcnow(), "http://www.tavendo.de/autobahn", str(autobahn.version)))
      f.write("""
      <table id="case_outcome_desc">
         <tr>
            <td class="case_ok">Pass</td>
            <td class="outcome_desc">Test case was executed and passed successfully.</td>
         </tr>
         <tr>
            <td class="case_non_strict">Non-Strict</td>
            <td class="outcome_desc">Test case was executed and passed non-strictly.
            A non-strict behavior is one that does not adhere to a SHOULD-behavior as described in the protocol specification or
            a well-defined, canonical behavior that appears to be desirable but left open in the protocol specification.
            An implementation with non-strict behavior is still conformant to the protocol specification.</td>
         </tr>
         <tr>
            <td class="case_failed">Fail</td>
            <td class="outcome_desc">Test case was executed and failed. An implementation which fails a test case - other
            than a performance/limits related one - is non-conforming to a MUST-behavior as described in the protocol specification.</td>
         </tr>
         <tr>
            <td class="case_missing">Missing</td>
            <td class="outcome_desc">Test case is missing, either because it was skipped via the test suite configuration
            or deactivated, i.e. because the implementation does not implement the tested feature or breaks during running
            the test case.</td>
         </tr>
      </table>
      """)
      f.write('      </div>\n')

      ## write big agent/case report table
      ##
      f.write('      <table id="agent_case_results">\n')

      ## sorted list of agents for which test cases where run
      ##
      agentList = sorted(self.agents.keys())

      ## create list ordered list of case Ids
      ##
      cl = []
      for c in Cases:
         t = caseClasstoIdTuple(c)
         cl.append((t, caseIdTupletoId(t)))
      cl = sorted(cl)
      caseList = []
      for c in cl:
         caseList.append(c[1])

      lastCaseCategory = None
      lastCaseSubCategory = None

      for caseId in caseList:

         caseCategoryIndex = caseId.split('.')[0]
         caseCategory = CaseCategories.get(caseCategoryIndex, "Misc")
         caseSubCategoryIndex = '.'.join(caseId.split('.')[:2])
         caseSubCategory = CaseSubCategories.get(caseSubCategoryIndex, None)

         ## Category/Agents row
         ##
         if caseCategory != lastCaseCategory or (self.repeatAgentRowPerSubcategory and caseSubCategory != lastCaseSubCategory):
            f.write('         <tr class="case_category_row">\n')
            f.write('            <td class="case_category">%s %s</td>\n' % (caseCategoryIndex, caseCategory))
            for agentId in agentList:
               f.write('            <td class="agent close_flex" colspan="2">%s</td>\n' % agentId)
            f.write('         </tr>\n')
            lastCaseCategory = caseCategory
            lastCaseSubCategory = None

         ## Subcategory row
         ##
         if caseSubCategory != lastCaseSubCategory:
            f.write('         <tr class="case_subcategory_row">\n')
            f.write('            <td class="case_subcategory" colspan="%d">%s %s</td>\n' % (len(agentList) * 2 + 1, caseSubCategoryIndex, caseSubCategory))
            f.write('         </tr>\n')
            lastCaseSubCategory = caseSubCategory

         ## Cases row
         ##
         f.write('         <tr class="agent_case_result_row">\n')
         f.write('            <td class="case"><a href="#case_desc_%s">Case %s</a></td>\n' % (caseId.replace('.', '_'), caseId))

         ## Case results
         ##
         for agentId in agentList:
            if self.agents[agentId].has_key(caseId):

               case = self.agents[agentId][caseId]

               agent_case_report_file = self.makeAgentCaseReportFilename(agentId, caseId)

               if case["behavior"] == Case.OK:
                  td_text = "Pass"
                  td_class = "case_ok"
               elif case["behavior"] == Case.NON_STRICT:
                  td_text = "Non-Strict"
                  td_class = "case_non_strict"
               elif case["behavior"] == Case.NO_CLOSE:
                  td_text = "No Close"
                  td_class = "case_no_close"
               else:
                  td_text = "Fail"
                  td_class = "case_failed"

               if case["behaviorClose"] == Case.OK:
                  ctd_text = "%s" % str(case["remoteCloseCode"])
                  ctd_class = "case_ok"
               elif case["behaviorClose"] == Case.FAILED_BY_CLIENT:
                  ctd_text = "%s" % str(case["remoteCloseCode"])
                  ctd_class = "case_almost"
               elif case["behaviorClose"] == Case.WRONG_CODE:
                  ctd_text = "%s" % str(case["remoteCloseCode"])
                  ctd_class = "case_non_strict"
               elif case["behaviorClose"] == Case.UNCLEAN:
                  ctd_text = "Unclean"
                  ctd_class = "case_failed"
               else:
                  ctd_text = "Fail"
                  ctd_class = "case_failed"

               if case["reportTime"]:
                  f.write('            <td class="%s"><a href="%s">%s</a><br/><span class="case_duration">%s ms</span></td><td class="close close_hide %s"><span class="close_code">%s</span></td>\n' % (td_class, agent_case_report_file, td_text, case["duration"],ctd_class,ctd_text))
               else:
                  f.write('            <td class="%s"><a href="%s">%s</a></td><td class="close close_hide %s"><span class="close_code">%s</span></td>\n' % (td_class, agent_case_report_file, td_text,ctd_class,ctd_text))

            else:
               f.write('            <td class="case_missing close_flex" colspan="2">Missing</td>\n')

         f.write("         </tr>\n")

      f.write("      </table>\n")
      f.write("      <br/><hr/>\n")

      ## Case descriptions
      ##
      f.write('      <div id="test_case_descriptions">\n')
      for caseId in caseList:
         CCase = CasesById[caseId]
         f.write('      <br/>\n')
         f.write('      <a name="case_desc_%s"></a>\n' % caseId.replace('.', '_'))
         f.write('      <h2>Case %s</h2>\n' % caseId)
         f.write('      <a class="up" href="#top">Up</a>\n')
         f.write('      <p class="case_text_block case_desc"><b>Case Description</b><br/><br/>%s</p>\n' % CCase.DESCRIPTION)
         f.write('      <p class="case_text_block case_expect"><b>Case Expectation</b><br/><br/>%s</p>\n' % CCase.EXPECTATION)
      f.write('      </div>\n')
      f.write("      <br/><hr/>\n")

      ## end of HTML
      ##
      f.write("   </body>\n")
      f.write("</html>\n")

      ## close created HTML file and return filename
      ##
      f.close()
      return report_filename


   def createAgentCaseReport(self, agentId, caseId, outdir):
      """
      Create case detail report HTML file.

      :param agentId: ID of agent for which to generate report.
      :type agentId: str
      :param caseId: ID of case for which to generate report.
      :type caseId: str
      :param outdir: Directory where to create file.
      :type outdir: str
      :returns: str -- Name of created file.
      """

      if not self.agents.has_key(agentId):
         raise Exception("no test data stored for agent %s" % agentId)

      if not self.agents[agentId].has_key(caseId):
         raise Exception("no test data stored for case %s with agent %s" % (caseId, agentId))

      ## get case to generate report for
      ##
      case = self.agents[agentId][caseId]

      ## open report file in create / write-truncate mode
      ##
      report_filename = self.makeAgentCaseReportFilename(agentId, caseId)
      f = open(os.path.join(outdir, report_filename), 'w')

      ## write HTML
      ##
      f.write('<!DOCTYPE html>\n')
      f.write('<html>\n')
      f.write('   <head>\n')
      f.write('      <meta charset="utf-8" />\n')
      f.write('      <style lang="css">%s</style>\n' % CSS_COMMON)
      f.write('      <style lang="css">%s</style>\n' % CSS_DETAIL_REPORT)
      f.write('   </head>\n')
      f.write('   <body>\n')
      f.write('      <a name="top"></a>\n')
      f.write('      <br/>\n')

      ## top logos
      f.write('      <center><img src="http://www.tavendo.de/static/autobahn/ws_protocol_test_report.png" border="0" width="820" height="46" alt="WebSockets Protocol Test Report"></img></a></center>\n')
      f.write('      <center><a href="http://www.tavendo.de/autobahn" title="Autobahn WebSockets"><img src="http://www.tavendo.de/static/autobahn/ws_protocol_test_report_autobahn.png" border="0" width="300" height="68" alt="Autobahn WebSockets"></img></a></center>\n')
      f.write('      <br/>\n')


      ## Case Summary
      ##
      if case["behavior"] == Case.OK:
         style = "case_ok"
         text = "Pass"
      elif case["behavior"] ==  Case.NON_STRICT:
         style = "case_non_strict"
         text = "Non-Strict"
      else:
         style = "case_failed"
         text = "Fail"
      f.write('      <p class="case %s">%s - <span style="font-size: 1.3em;"><b>Case %s</b></span> : %s - <span style="font-size: 0.9em;"><b>%d</b> ms @ %s</a></p>\n' % (style, case["agent"], caseId, text, case["duration"], case["started"]))


      ## Case Description, Expectation, Outcome, Case Closing Behavior
      ##
      f.write('      <p class="case_text_block case_desc"><b>Case Description</b><br/><br/>%s</p>\n' % case["description"])
      f.write('      <p class="case_text_block case_expect"><b>Case Expectation</b><br/><br/>%s</p>\n' % case["expectation"])
      f.write("""
      <p class="case_text_block case_outcome">
         <b>Case Outcome</b><br/><br/>%s<br/><br/>
         <i>Expected:</i><br/><span class="case_pickle">%s</span><br/><br/>
         <i>Observed:</i><br><span class="case_pickle">%s</span>
      </p>\n""" % (case.get("result", ""), self.limitString(case.get("expected", ""), FuzzingFactory.MAX_CASE_PICKLE_LEN), self.limitString(case.get("received", ""), FuzzingFactory.MAX_CASE_PICKLE_LEN)))
      f.write('      <p class="case_text_block case_closing_beh"><b>Case Closing Behavior</b><br/><br/>%s (%s)</p>\n' % (case.get("resultClose", ""), case.get("behaviorClose", "")))
      f.write("      <br/><hr/>\n")


      ## Closing Behavior
      ##
      f.write('      <h2>Closing Behavior</h2>\n')
      f.write('      <table>\n')
      f.write('         <tr class="stats_header"><td>Key</td><td class="left">Value</td></tr>\n')
      f.write('         <tr class="stats_row"><td>isServer</td><td class="left">%s</td></tr>\n' % case["isServer"])
      f.write('         <tr class="stats_row"><td>closedByMe</td><td class="left">%s</td></tr>\n' % case["closedByMe"])
      f.write('         <tr class="stats_row"><td>failedByMe</td><td class="left">%s</td></tr>\n' % case["failedByMe"])
      f.write('         <tr class="stats_row"><td>droppedByMe</td><td class="left">%s</td></tr>\n' % case["droppedByMe"])
      f.write('         <tr class="stats_row"><td>wasClean</td><td class="left">%s</td></tr>\n' % case["wasClean"])
      f.write('         <tr class="stats_row"><td>wasNotCleanReason</td><td class="left">%s</td></tr>\n' % case["wasNotCleanReason"])
      f.write('         <tr class="stats_row"><td>wasServerConnectionDropTimeout</td><td class="left">%s</td></tr>\n' % case["wasServerConnectionDropTimeout"])
      f.write('         <tr class="stats_row"><td>wasCloseHandshakeTimeout</td><td class="left">%s</td></tr>\n' % case["wasCloseHandshakeTimeout"])
      f.write('         <tr class="stats_row"><td>localCloseCode</td><td class="left">%s</td></tr>\n' % str(case["localCloseCode"]))
      f.write('         <tr class="stats_row"><td>localCloseReason</td><td class="left">%s</td></tr>\n' % str(case["localCloseReason"]))
      f.write('         <tr class="stats_row"><td>remoteCloseCode</td><td class="left">%s</td></tr>\n' % str(case["remoteCloseCode"]))
      f.write('         <tr class="stats_row"><td>remoteCloseReason</td><td class="left">%s</td></tr>\n' % case["remoteCloseReason"])
      f.write('      </table>')
      f.write("      <br/><hr/>\n")


      ## Wire Statistics
      ##
      f.write('      <h2>Wire Statistics</h2>\n')
      if not case["createStats"]:
         f.write('      <p style="margin-left: 40px; color: #f00;"><i>Statistics for octets/frames disabled!</i></p>\n')
      else:
         ## octet stats
         ##
         for statdef in [("Received", case["rxOctetStats"]), ("Transmitted", case["txOctetStats"])]:
            f.write('      <h3>Octets %s by Chop Size</h3>\n' % statdef[0])
            f.write('      <table>\n')
            stats = statdef[1]
            total_cnt = 0
            total_octets = 0
            f.write('         <tr class="stats_header"><td>Chop Size</td><td>Count</td><td>Octets</td></tr>\n')
            for s in sorted(stats.keys()):
               f.write('         <tr class="stats_row"><td>%d</td><td>%d</td><td>%d</td></tr>\n' % (s, stats[s], s * stats[s]))
               total_cnt += stats[s]
               total_octets += s * stats[s]
            f.write('         <tr class="stats_total"><td>Total</td><td>%d</td><td>%d</td></tr>\n' % (total_cnt, total_octets))
            f.write('      </table>\n')

         ## frame stats
         ##
         for statdef in [("Received", case["rxFrameStats"]), ("Transmitted", case["txFrameStats"])]:
            f.write('      <h3>Frames %s by Opcode</h3>\n' % statdef[0])
            f.write('      <table>\n')
            stats = statdef[1]
            total_cnt = 0
            f.write('         <tr class="stats_header"><td>Opcode</td><td>Count</td></tr>\n')
            for s in sorted(stats.keys()):
               f.write('         <tr class="stats_row"><td>%d</td><td>%d</td></tr>\n' % (s, stats[s]))
               total_cnt += stats[s]
            f.write('         <tr class="stats_total"><td>Total</td><td>%d</td></tr>\n' % (total_cnt))
            f.write('      </table>\n')
      f.write("      <br/><hr/>\n")


      ## Wire Log
      ##
      f.write('      <h2>Wire Log</h2>\n')
      if not case["createWirelog"]:
         f.write('      <p style="margin-left: 40px; color: #f00;"><i>Wire log after handshake disabled!</i></p>\n')

      f.write('      <div id="wirelog">\n')
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

         elif t[0] in ["CT", "CTE", "KL", "KLE", "TI", "TIE", "WLM"]:
            pass

         else:
            raise Exception("logic error (unrecognized wire log row type %s - row %s)" % (t[0], str(t)))

         if t[0] in ["RO", "TO", "RF", "TF"]:

            lines = textwrap.wrap(t[1], 100)
            if t[0] in ["RO", "TO"]:
               if len(lines) > 0:
                  f.write('         <pre class="%s">%03d %s: %s</pre>\n' % (css_class, i, prefix, lines[0]))
                  for ll in lines[1:]:
                     f.write('         <pre class="%s">%s%s</pre>\n' % (css_class, (2+4+len(prefix))*" ", ll))
            else:
               if t[0] == "RF":
                  if t[6]:
                     mmask = binascii.b2a_hex(t[6])
                  else:
                     mmask = str(t[6])
                  f.write('         <pre class="%s">%03d %s: OPCODE=%s, FIN=%s, RSV=%s, MASKED=%s, MASK=%s</pre>\n' % (css_class, i, prefix, str(t[2]), str(t[3]), str(t[4]), str(t[5]), mmask))
               elif t[0] == "TF":
                  f.write('         <pre class="%s">%03d %s: OPCODE=%s, FIN=%s, RSV=%s, MASK=%s, PAYLOAD-REPEAT-LEN=%s, CHOPSIZE=%s, SYNC=%s</pre>\n' % (css_class, i, prefix, str(t[2]), str(t[3]), str(t[4]), str(t[5]), str(t[6]), str(t[7]), str(t[8])))
               else:
                  raise Exception("logic error")
               for ll in lines:
                  f.write('         <pre class="%s">%s%s</pre>\n' % (css_class, (2+4+len(prefix))*" ", ll))

         elif t[0] == "WLM":
            if t[1]:
               f.write('         <pre class="wirelog_delay">%03d WIRELOG ENABLED</pre>\n' % (i))
            else:
               f.write('         <pre class="wirelog_delay">%03d WIRELOG DISABLED</pre>\n' % (i))

         elif t[0] == "CT":
            f.write('         <pre class="wirelog_delay">%03d DELAY %f sec for TAG %s</pre>\n' % (i, t[1], t[2]))

         elif t[0] == "CTE":
            f.write('         <pre class="wirelog_delay">%03d DELAY TIMEOUT on TAG %s</pre>\n' % (i, t[1]))

         elif t[0] == "KL":
            f.write('         <pre class="wirelog_kill_after">%03d FAIL CONNECTION AFTER %f sec</pre>\n' % (i, t[1]))

         elif t[0] == "KLE":
            f.write('         <pre class="wirelog_kill_after">%03d FAILING CONNECTION</pre>\n' % (i))

         elif t[0] == "TI":
            f.write('         <pre class="wirelog_kill_after">%03d CLOSE CONNECTION AFTER %f sec</pre>\n' % (i, t[1]))

         elif t[0] == "TIE":
            f.write('         <pre class="wirelog_kill_after">%03d CLOSING CONNECTION</pre>\n' % (i))

         else:
            raise Exception("logic error (unrecognized wire log row type %s - row %s)" % (t[0], str(t)))

         i += 1

      if case["droppedByMe"]:
         f.write('         <pre class="wirelog_tcp_closed_by_me">%03d TCP DROPPED BY ME</pre>\n' % i)
      else:
         f.write('         <pre class="wirelog_tcp_closed_by_peer">%03d TCP DROPPED BY PEER</pre>\n' % i)
      f.write('      </div>\n')
      f.write("      <br/><hr/>\n")

      ## end of HTML
      ##
      f.write("   </body>\n")
      f.write("</html>\n")

      ## close created HTML file and return filename
      ##
      f.close()
      return report_filename



class FuzzingServerProtocol(FuzzingProtocol, WebSocketServerProtocol):

   def connectionMade(self):
      WebSocketServerProtocol.connectionMade(self)
      FuzzingProtocol.connectionMade(self)


   def connectionLost(self, reason):
      WebSocketServerProtocol.connectionLost(self, reason)
      FuzzingProtocol.connectionLost(self, reason)


   def onConnect(self, connectionRequest):
      if self.debug:
         log.msg("connection received from %s for host %s, path %s, parms %s, origin %s, protocols %s" % (connectionRequest.peerstr, connectionRequest.host, connectionRequest.path, str(connectionRequest.params), connectionRequest.origin, str(connectionRequest.protocols)))

      if connectionRequest.params.has_key("agent"):
         if len(connectionRequest.params["agent"]) > 1:
            raise Exception("multiple agents specified")
         self.caseAgent = connectionRequest.params["agent"][0]

      if connectionRequest.params.has_key("case"):
         if len(connectionRequest.params["case"]) > 1:
            raise Exception("multiple test cases specified")
         try:
            self.case = int(connectionRequest.params["case"][0])
         except:
            raise Exception("invalid test case ID %s" % connectionRequest.params["case"][0])

      if self.case:
         if self.case >= 1 and self.case <= len(self.factory.specCases):
            self.Case = CasesById[self.factory.specCases[self.case - 1]]
            self.runCase = self.Case(self)
         else:
            raise Exception("case %s not found" % self.case)

      if connectionRequest.path == "/runCase":
         if not self.runCase:
            raise Exception("need case to run")
         if not self.caseAgent:
            raise Exception("need agent to run case")
         self.caseStarted = utcnow()
         print "Running test case ID %s for agent %s from peer %s" % (caseClasstoId(self.Case), self.caseAgent, connectionRequest.peerstr)

      elif connectionRequest.path == "/updateReports":
         if not self.caseAgent:
            raise Exception("need agent to update reports for")
         print "Updating reports, requested by peer %s" % connectionRequest.peerstr

      elif connectionRequest.path == "/getCaseCount":
         pass

      else:
         print "Entering direct command mode for peer %s" % connectionRequest.peerstr

      self.path = connectionRequest.path

      return None


class FuzzingServerFactory(FuzzingFactory, WebSocketServerFactory):

   protocol = FuzzingServerProtocol

   def __init__(self, spec):

      debug = spec.get("debug", False)
      debugCodePaths = spec.get("debugCodePaths", False)

      WebSocketServerFactory.__init__(self, debug = debug, debugCodePaths = debugCodePaths)
      FuzzingFactory.__init__(self, debug = debug, outdir = spec.get("outdir", "./reports/clients/"))

      ## WebSocket session parameters
      ##
      self.setSessionParameters(url = spec["url"],
                                protocols = spec.get("protocols", []),
                                server = "AutobahnWebSocketsTestSuite/%s" % autobahn.version)

      ## WebSocket protocol options
      ##
      self.setProtocolOptions(**spec.get("options", {}))

      self.spec = spec
      self.specCases = parseSpecCases(self.spec)
      print "Autobahn WebSockets %s Fuzzing Server" % autobahn.version
      print "Ok, will run %d test cases for any clients connecting" % len(self.specCases)
      print "Cases = %s" % str(self.specCases)


class FuzzingClientProtocol(FuzzingProtocol, WebSocketClientProtocol):

   def connectionMade(self):
      FuzzingProtocol.connectionMade(self)
      WebSocketClientProtocol.connectionMade(self)

      self.caseAgent = self.factory.agent
      self.case = self.factory.currentCaseIndex
      self.Case = Cases[self.case - 1]
      self.runCase = self.Case(self)
      self.caseStarted = utcnow()
      print "Running test case ID %s for agent %s from peer %s" % (caseClasstoId(self.Case), self.caseAgent, self.peerstr)


   def connectionLost(self, reason):
      WebSocketClientProtocol.connectionLost(self, reason)
      FuzzingProtocol.connectionLost(self, reason)


class FuzzingClientFactory(FuzzingFactory, WebSocketClientFactory):

   protocol = FuzzingClientProtocol

   def __init__(self, spec):

      debug = spec.get("debug", False)
      debugCodePaths = spec.get("debugCodePaths", False)

      WebSocketClientFactory.__init__(self, debug = debug, debugCodePaths = debugCodePaths)
      FuzzingFactory.__init__(self, debug = debug, outdir = spec.get("outdir", "./reports/servers/"))

      self.spec = spec
      self.specCases = parseSpecCases(self.spec)
      print "Autobahn WebSockets %s Fuzzing Client" % autobahn.version
      print "Ok, will run %d test cases against %d servers" % (len(self.specCases), len(spec["servers"]))
      print "Cases = %s" % str(self.specCases)
      print "Servers = %s" % str([x["url"] + "@" + x["agent"] for x in spec["servers"]])

      self.currServer = -1
      if self.nextServer():
         if self.nextCase():
            connectWS(self)


   def nextServer(self):
      self.currSpecCase = -1
      self.currServer += 1
      if self.currServer < len(self.spec["servers"]):
         ## run tests for next server
         ##
         server = self.spec["servers"][self.currServer]

         ## agent (=server) string for reports
         ##
         self.agent = server.get("agent", "UnknownServer")
         if self.agent == "AutobahnServer":
            self.agent = "AutobahnServer/%s" % autobahn.version

         ## WebSocket session parameters
         ##
         self.setSessionParameters(url = server["url"],
                                   origin = server.get("origin", None),
                                   protocols = server.get("protocols", []),
                                   useragent = "AutobahnWebSocketsTestSuite/%s" % autobahn.version)

         ## WebSocket protocol options
         ##
         self.resetProtocolOptions() # reset to defaults
         self.setProtocolOptions(**self.spec.get("options", {})) # set spec global options
         self.setProtocolOptions(**server.get("options", {})) # set server specific options
         return True
      else:
         return False


   def nextCase(self):
      self.currSpecCase += 1
      if self.currSpecCase < len(self.specCases):
         self.currentCaseId = self.specCases[self.currSpecCase]
         self.currentCaseIndex = CasesIndices[self.currentCaseId]
         return True
      else:
         return False


   def clientConnectionLost(self, connector, reason):
      if self.nextCase():
         connector.connect()
      else:
         if self.nextServer():
            if self.nextCase():
               connectWS(self)
         else:
            self.createReports()
            reactor.stop()
