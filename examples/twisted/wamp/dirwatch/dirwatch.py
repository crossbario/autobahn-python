###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
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
import threading


if sys.platform == 'win32':
   from win32.dirwatch import DirWatcher
else:
   raise ImportError("missing platform support for %s" % sys.platform)


from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import connectWS
from autobahn.wamp import WampClientFactory, \
                          WampClientProtocol



class DirWatchClientProtocol(WampClientProtocol):

   def onSessionOpen(self):
      print "Connected", threading.currentThread().name
      self.factory.wasConnected = True



class DirWatchClientFactory(WampClientFactory):

   def __init__(self, app):
      WampClientFactory.__init__(self, app.url, debugWamp = app.debug)
      self.app = app
      self.proto = None
      self.wasConnected = False


   def buildProtocol(self, addr):
      self.proto = DirWatchClientProtocol()
      self.proto.factory = self
      return self.proto


   def _reconnect(self, connector):
      if self.wasConnected:
         log.msg("reconnecting in 2 secs ..")
         reactor.callLater(2, connector.connect)
      else:
         if self.app.watcher:
            self.app.watcher.stop()
         reactor.stop()


   def clientConnectionLost(self, connector, reason):
      self.proto = None
      log.msg("connection lost: %s" % reason)
      self._reconnect(connector)


   def clientConnectionFailed(self, connector, reason):
      self.proto = None
      log.msg("connection failed: %s" % reason)
      self._reconnect(connector)



class DirWatcherApp:

   def __init__(self, url, directory = ".", debug = False):
      self.directory = directory
      self.url = url
      self.debug = debug
      self.client = None
      self.watcher = None
      self.seq = 0


   def onDirEvent(self, events):
      print threading.currentThread().name, events

      ## only publish when we are connected to WAMP server
      ##
      if self.client and self.client.proto:
         for e in events:
            self.seq += 1
            event = {'operation': e[0],
                     'path': e[1],
                     'sequence': self.seq}

            ## we MUST use callFromThread to publish our event, since
            ## the code here is running on a background thread, and
            ## event dispatching (and in general the Twisted reactor)
            ## runs on the main thread.
            ##
            reactor.callFromThread(self.client.proto.publish, u"http://dirwatch.autobahn.ws#filesystemEvent", event)
      else:
         log.msg("not connected - skipping event")


   def start(self):
      ## the directory watcher
      ##
      self.watcher = DirWatcher(dir = self.directory)

      ## start directory watcher on _background_ thread
      ##
      reactor.callInThread(self.watcher.loop, self.onDirEvent)

      ## start WAMP client (on main reactor thread)
      ##
      self.client = DirWatchClientFactory(self)
      connectWS(self.client)



if __name__ == '__main__':

   log.startLogging(sys.stdout)
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'

   app = DirWatcherApp("ws://localhost:9000", ".", debug)
   app.start()

   reactor.run()
