###############################################################################
##
##  Copyright (C) 2012-2013 Tavendo GmbH
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


import sys, time

if sys.platform == 'win32':
   ## on windows, we need to use the following reactor for serial support
   ## http://twistedmatrix.com/trac/ticket/3802
   ##
   from twisted.internet import win32eventreactor
   win32eventreactor.install()

from twisted.internet import reactor
print "Using Twisted reactor", reactor.__class__
print

from twisted.python import usage, log
from twisted.protocols.basic import LineReceiver
from twisted.internet.serialport import SerialPort
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc


class Serial2WsOptions(usage.Options):
   
   optFlags = [
      ['debugserial', 'd', 'Turn on Serial data logging.'],
      ['debugwamp', 't', 'Turn on WAMP traffic logging.'],
      ['debugws', 'r', 'Turn on WebSocket traffic logging.']
   ]

   optParameters = [
      ['baudrate', 'b', 9600, 'Serial baudrate'],
      ['port', 'p', 3, 'Serial port to use (e.g. 3 for a COM port on Windows, /dev/ttyATH0 for Arduino Yun, /dev/ttyACM0 for Serial-over-USB on RaspberryPi'],
      ['webport', 'w', 8080, 'Web port to use for embedded Web server'],
      ['wsurl', 's', "ws://localhost:9000", 'WebSocket port to use for embedded WebSocket server']
   ]


## MCU protocol
##
class McuProtocol(LineReceiver):

   ## need a reference to our WS-MCU gateway factory to dispatch PubSub events
   ##
   def __init__(self, wsMcuFactory):
      self.wsMcuFactory = wsMcuFactory


   ## this method is exported as RPC and can be called by connected clients
   ##
   @exportRpc("control-led")
   def controlLed(self, status):
      if status:
         payload = '1'
      else:
         payload = '0'
      if self.wsMcuFactory.debugSerial:
         print "Serial TX:", payload
      self.transport.write(payload)


   def connectionMade(self):
      log.msg('Serial port connected.')


   def lineReceived(self, line):
      if self.wsMcuFactory.debugSerial:
         print "Serial RX:", line
      try:
         ## parse data received from MCU
         ##
         data = [int(x) for x in line.split()]

         ## construct PubSub event from raw data
         ##
         evt = {'id': data[0], 'value': data[1]}

         ## publish event to all clients subscribed to topic
         ##
         self.wsMcuFactory.dispatch("http://example.com/mcu#analog-value", evt)

      except ValueError:
         log.err('Unable to parse value %s' % line)


## WS-MCU protocol
##
class WsMcuProtocol(WampServerProtocol):

   def onSessionOpen(self):
      ## register topic prefix under which we will publish MCU measurements
      ##
      self.registerForPubSub("http://example.com/mcu#", True)

      ## register methods for RPC
      ##
      self.registerForRpc(self.factory.mcuProtocol, "http://example.com/mcu-control#")


## WS-MCU factory
##
class WsMcuFactory(WampServerFactory):

   protocol = WsMcuProtocol

   def __init__(self, url, debugSerial = False, debugWs = False, debugWamp = False):
      WampServerFactory.__init__(self, url, debug = debugWs, debugWamp = debugWamp)
      self.debugSerial = debugSerial
      self.mcuProtocol = McuProtocol(self)


if __name__ == '__main__':

   ## parse options
   ##
   o = Serial2WsOptions()
   try:
      o.parseOptions()
   except usage.UsageError, errortext:
      print '%s %s' % (sys.argv[0], errortext)
      print 'Try %s --help for usage details' % sys.argv[0]
      sys.exit(1)

   debugWs = bool(o.opts['debugws'])
   debugWamp = bool(o.opts['debugwamp'])
   debugSerial = bool(o.opts['debugserial'])
   baudrate = int(o.opts['baudrate'])
   port = o.opts['port']
   webport = int(o.opts['webport'])
   wsurl = o.opts['wsurl']

   ## start Twisted log system
   ##
   log.startLogging(sys.stdout)

   ## create Serial2Ws gateway factory
   ##
   wsMcuFactory = WsMcuFactory(wsurl, debugSerial = debugSerial, debugWs = debugWs, debugWamp = debugWamp)
   listenWS(wsMcuFactory)

   ## create serial port and serial port protocol
   ##
   log.msg('About to open serial port %s [%d baud] ..' % (port, baudrate))
   serialPort = SerialPort(wsMcuFactory.mcuProtocol, port, reactor, baudrate = baudrate)

   ## create embedded web server for static files
   ##
   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(webport, web)

   ## start Twisted reactor ..
   ##
   reactor.run()
