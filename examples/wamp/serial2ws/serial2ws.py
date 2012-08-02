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

from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc


class Serial2WsOptions(usage.Options):
   optParameters = [
      ['baudrate', 'b', 9600, 'Serial baudrate'],
      ['port', 'p', 3, 'Serial port to use'],
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
         print "turn on LED"
         self.transport.write('1')
      else:
         print "turn off LED"
         self.transport.write('0')


   def connectionMade(self):
      log.msg('Serial port connected.')


   def lineReceived(self, line):
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

         log.msg("Analog value: %s" % str(evt));
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

   def __init__(self, url):
      WampServerFactory.__init__(self, url)
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

   baudrate = int(o.opts['baudrate'])
   port = int(o.opts['port'])
   webport = int(o.opts['webport'])
   wsurl = o.opts['wsurl']

   ## start Twisted log system
   ##
   log.startLogging(sys.stdout)

   ## create Serial2Ws gateway factory
   ##
   wsMcuFactory = WsMcuFactory(wsurl)
   listenWS(wsMcuFactory)

   ## create serial port and serial port protocol
   ##
   log.msg('About to open serial port %d [%d baud] ..' % (port, baudrate))
   serialPort = SerialPort(wsMcuFactory.mcuProtocol, port, reactor, baudrate = baudrate)

   ## create embedded web server for static files
   ##
   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(webport, web)

   ## start Twisted reactor ..
   ##
   reactor.run()
