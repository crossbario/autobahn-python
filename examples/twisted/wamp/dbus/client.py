###############################################################################
##
##  Copyright (C) 2012-2014 Tavendo GmbH
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

from twisted.python import log
from twisted.internet import reactor, defer

from txdbus import error, client

from autobahn.twisted.websocket import connectWS

from autobahn.wamp1.protocol import WampClientFactory, \
                                    WampCraClientProtocol


def delay(t):
   d = defer.Deferred()
   reactor.callLater(t, lambda : d.callback(None) )
   return d


class DbusClientProtocol(WampCraClientProtocol):

   def onSessionOpen(self):
      self.authenticate(self.onAuthSuccess,
                        self.onAuthError,
                        authKey = self.factory.user,
                        authSecret = self.factory.password)


   def onClose(self, wasClean, code, reason):
      reactor.stop()


   def onAuthSuccess(self, permissions):
      print "Authentication Success!", permissions
      self.subscribe("http://example.com/topics/%s" % self.factory.user, self.onNotify)
      self.subscribe("http://example.com/topics/all", self.onNotify)


   def onAuthError(self, uri, desc, details):
      print "Authentication Error!", uri, desc, details
      self.sendClose()


   @defer.inlineCallbacks
   def onNotify(self, topic, event):
      print topic, event

      con = yield client.connect(reactor, 'session')

      notifier = yield con.getRemoteObject('org.freedesktop.Notifications',
                                           '/org/freedesktop/Notifications')

      nid = yield notifier.callRemote('Notify',
                                      str(event['app']), 0,
                                      '',
                                      str(event['title']),
                                      str(event['body']),
                                      [], dict(),
                                      1)

      yield delay(event['duration'])

      print "autoclosing notification"

      yield notifier.callRemote('CloseNotification', nid)


class DbusClientFactory(WampClientFactory):

   protocol = DbusClientProtocol

   def __init__(self, wsuri, user, password):
      self.user = user
      self.password = password
      WampClientFactory.__init__(self, wsuri)



if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = DbusClientFactory(sys.argv[1], sys.argv[2], sys.argv[3])
   connectWS(factory)
   reactor.run()
