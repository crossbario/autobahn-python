###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
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

from __future__ import absolute_import

from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import clientFromString
from twisted.words.protocols import irc

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError

from wampirc.client import IRCClientFactory


class Bot:
   """
   Tracks currently running bot instances.
   """
   def __init__(self, id, factory, client):
      self.id = id
      self.factory = factory
      self.client = client


class IRCComponent(ApplicationSession):
   """
   IRC bot services component.
   """

   def __init__(self, config):
      ApplicationSession.__init__(self)
      self.config = config
      self._bots = {}
      self._bot_no = 0

   @wamp.procedure('com.myapp.start_bot')
   def start_bot(self, nick, channels):
      self._bot_no += 1
      id = self._bot_no
      factory = IRCClientFactory(self, nick, channels)

      from twisted.internet import reactor
      client = clientFromString(reactor, self.config.extra['server'])
      d = client.connect(factory)

      def onconnect(res):
         self._bots[id] = Bot(id, factory, client)
         return id
      d.addCallback(onconnect)

      return d

   @wamp.procedure('com.myapp.stop_bot')
   def stop_bot(self, id):
      if id in self._bots:
         f = self._bots[id].factory
         if f.proto:
            f.proto.transport.loseConnection()
         f.stopFactory()
         del self._bots[id]
      else:
         raise ApplicationError('com.myapp.error.no_such_bot')

   def onConnect(self):
      self.join(self.config.realm)

   @inlineCallbacks
   def onJoin(self, details):
      try:
         regs = yield self.register(self)
         print("Ok, registered {} procedures.".format(len(regs)))
      except Exception as e:
         print("Failed to register procedures: {}".format(e))

      print("IRC Bot Backend ready!")

   def onLeave(self, details):
      self.disconnect()

   def onDisconnect(self):
      reactor.stop()



def make(config):
   if config:
      return IRCComponent(config)
   else:
      ## if no config given, return a description of this WAMPlet ..
      return {'label': 'An IRC bot service component',
              'description': 'This component provides IRC bot services via WAMP.'}



if __name__ == '__main__':
   from autobahn.twisted.wamp import ApplicationRunner

   extra = {
      "server": "tcp:irc.freenode.net:6667"
   }

   ## test drive the component during development ..
   runner = ApplicationRunner(endpoint = "tcp:127.0.0.1:8080",
      url = "ws://localhost:8080/ws",
      realm = "realm1",
      extra = extra,
      debug = False,       ## low-level WebSocket debugging
      debug_wamp = False,  ## WAMP protocol-level debugging
      debug_app = True)    ## app-level debugging

   runner.run(make)
