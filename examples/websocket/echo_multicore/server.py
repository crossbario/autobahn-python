###############################################################################
##
##  Copyright 2013 (C) Tavendo GmbH
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

## make sure we run a capable OS/reactor
##
startupMsgs = []
if 'bsd' in sys.platform:
   from twisted.internet import kqreactor
   kqreactor.install()
   startupMsgs.append("Alrighty: you run a capable kqueue platform - good job!")
elif sys.platform.startswith('linux'):
   from twisted.internet import epollreactor
   epollreactor.install()
   startupMsgs.append("Alrighty: you run a capable epoll platform - good job!")
elif sys.platform.startswith('darwin'):
   from twisted.internet import kqreactor
   kqreactor.install()
   startupMsgs.append("Huh, you run OSX and have kqueue, but don't be disappointed when performance sucks;)")
elif sys.platform == 'win32':
   raise Exception("Sorry dude, Twisted/Windows select/iocp reactors lack the necessary bits.")
else:
   raise Exception("Hey man, what OS are you using?")

import pkg_resources
from twisted.internet import reactor
startupMsgs.append("Using Twisted reactor class %s on Twisted %s" % (str(reactor.__class__), pkg_resources.require("Twisted")[0].version))


import sys, os
import StringIO
from os import environ
from sys import argv, executable
from socket import AF_INET

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               parseWsUrl


class Stats:
   def __init__(self):
      self.period = 1
      self.msgs = 0
      self.octets = 0
      self.clients = 0
      self.handshakes = 0

   def __repr__(self):
      return ("connected clients:    %d\n" + \
              "total handshakes:     %d\n" + \
              "total echo'ed msgs:   %d\n" + \
              "total echo'ed octets: %d\n") % (self.clients, self.handshakes, self.msgs, self.octets)



class EchoServerProtocol(WebSocketServerProtocol):

   def onOpen(self):
      self.factory.stats.clients += 1
      self.factory.stats.handshakes += 1

   def onMessage(self, msg, binary):
      self.sendMessage(msg, binary)
      self.factory.stats.msgs += 1
      self.factory.stats.octets += len(msg)

   def onClose(self, wasClean, code, reason):
      self.factory.stats.clients -= 1



class EchoServerFactory(WebSocketServerFactory):

   protocol = EchoServerProtocol

   def __init__(self, wsuri, debug = False):
      WebSocketServerFactory.__init__(self, wsuri, debug = debug, debugCodePaths = debug)
      self.stats = Stats()



def master(options):
   """
   Start of the master process.
   """
   if not options.silence:
      print "Master started on PID %s" % os.getpid()

   ## start embedded Web server if asked for (this only runs on master)
   ##
   if options.port:
      webdir = File(".")
      web = Site(webdir)
      web.log = lambda _: None # disable annoyingly verbose request logging
      reactor.listenTCP(options.port, web)

   ## we just need some factory like thing .. it won't be used on master anyway
   ## for actual socket accept
   ##
   factory = Factory()

   ## create socket, bind and listen ..
   port = reactor.listenTCP(options.wsport, factory, backlog = options.backlog)

   ## .. but immediately stop reading: we only want to accept on workers, not master
   port.stopReading()

   ## fire off background workers
   ##
   for i in range(options.workers):

      args = [executable, __file__, "--fd", str(port.fileno())]

      ## pass on cmd line args to worker ..
      args.extend(sys.argv[1:])

      reactor.spawnProcess(
         None, executable, args,
         childFDs = {0: 0, 1: 1, 2: 2, port.fileno(): port.fileno()},
         env = environ)

   reactor.run()


def worker(options):
   """
   Start background worker process.
   """
   workerPid = os.getpid()

   factory = EchoServerFactory(options.wsuri, debug = options.debug)

   ## The master already created the socket, just start listening and accepting
   ##
   port = reactor.adoptStreamPort(options.fd, AF_INET, factory)

   if not options.silence:
      print "Worker started on PID %s using factory %s and protocol %s" % (workerPid, factory, factory.protocol)

   if not options.silence:
      def stat():
         output = StringIO.StringIO()
         output.write("-" * 80 + "\n")
         output.write("Worker PID %s stats for period %d:\n\n%s"  % (workerPid, factory.stats.period, factory.stats))
         factory.stats.period += 1
         output.write("-" * 80 + "\n\n")
         sys.stdout.write(output.getvalue())
         reactor.callLater(options.interval, stat)

      reactor.callLater(options.interval, stat)

   reactor.run()


if __name__ == '__main__':

   import argparse

   parser = argparse.ArgumentParser(description = 'Autobahn WebSocket Echo Multicore Server')
   parser.add_argument('--wsuri', dest = 'wsuri', type = str, default = 'ws://localhost:9000', help = 'The WebSocket URI the server is listening on, e.g. ws://localhost:9000.')
   parser.add_argument('--port', dest = 'port', type = int, default = 8080, help = 'Port to listen on for embedded Web server. Set to 0 to disable.')
   parser.add_argument('--workers', dest = 'workers', type = int, default = 4, help = 'Number of workers to spawn - should fit the number of (phyisical) CPU cores.')
   parser.add_argument('--backlog', dest = 'backlog', type = int, default = 8192, help = 'TCP accept queue depth. You must tune your OS also as this is just advisory!')
   parser.add_argument('--silence', dest = 'silence', action = "store_true", default = False, help = 'Silence log output.')
   parser.add_argument('--debug', dest = 'debug', action = "store_true", default = False, help = 'Enable WebSocket debug output.')
   parser.add_argument('--interval', dest = 'interval', type = int, default = 5, help = 'Worker stats update interval.')

   parser.add_argument('--fd', dest = 'fd', type = int, default = None, help = 'If given, this is a worker which will use provided FD and all other options are ignored.')

   options = parser.parse_args()

   ## parse WS URI into components and forward via options
   ## FIXME: add TLS support
   isSecure, host, wsport, resource, path, params = parseWsUrl(options.wsuri)
   options.wsport = wsport

   #if not options.silence:
   #   log.startLogging(sys.stdout)

   if options.fd is not None:
      # run worker
      worker(options)
   else:
      if not options.silence:
         for m in startupMsgs:
            print m
      # run master
      master(options)
