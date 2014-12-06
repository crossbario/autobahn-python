import sys

from twisted.python import log
from twisted.internet.endpoints import clientFromString

from autobahn.twisted.choosereactor import install_reactor
from autobahn.twisted.websocket import WampWebSocketClientFactory
from autobahn.twisted.wamp import ApplicationSessionFactory
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp import types


class MySession(ApplicationSession):

    def onJoin(self, details):
      print("Session attached to realm!")



log.startLogging(sys.stdout)

reactor = install_reactor()

print("Running on reactor {}".format(reactor))

session_factory = ApplicationSessionFactory(types.ComponentConfig(realm = u"realm1"))
session_factory.session = MySession

transport_factory = WampWebSocketClientFactory(session_factory, url = "ws://localhost", debug = True)

client = clientFromString(reactor, "unix:/tmp/cbsocket")
client.connect(transport_factory)
reactor.run()
