# coding=utf-8

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

from case import Case
from autobahn.websocket import WebSocketProtocol
import binascii
from zope.interface import implements
from twisted.internet import reactor, interfaces


class FrameProducer:

   implements(interfaces.IPushProducer)

   def __init__(self, proto, payload):
      self.proto = proto
      self.payload = payload
      self.paused = False
      self.stopped = False

   def pauseProducing(self):
      self.paused = True

   def resumeProducing(self):
      if self.stopped:
         return
      self.paused = False
      while not self.paused:
         self.proto.sendMessageFrame(self.payload)

   def stopProducing(self):
      self.stopped = True


class Case9_9_1(Case):

   PAYLOAD = "*" * 2**10 * 4

   DESCRIPTION = """Send a text message consisting of an infinite sequence of frames with payload 4k. Do this for X seconds."""

   EXPECTATION = """..."""

   def onOpen(self):

      self.expected[Case.OK] = [("timeout", "A"), ("timeout", "B")]
      self.expectedClose = {"closedByMe": True, "closeCode": [self.p.CLOSE_STATUS_CODE_NORMAL], "requireClean": True}

      self.p.createWirelog = False
      self.producer = FrameProducer(self.p, self.PAYLOAD)
      self.p.registerProducer(self.producer, True)
      self.p.beginMessage(opcode = WebSocketProtocol.MESSAGE_TYPE_TEXT)
      self.producer.resumeProducing()
      self.p.continueLater(3, self.part2, "A")

   def part2(self):
      self.received.append(("timeout", "A"))
      self.producer.stopProducing()
      self.p.endMessage()
      self.p.continueLater(5, self.part3, "B")

   def part3(self):
      self.received.append(("timeout", "B"))
      self.p.createWirelog = True
      self.p.sendClose(WebSocketProtocol.CLOSE_STATUS_CODE_NORMAL, "You have survived;)")

   def onConnectionLost(self, failedByMe):
      self.producer.stopProducing()
      Case.onConnectionLost(self, failedByMe)
