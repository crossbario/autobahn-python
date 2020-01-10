from twisted.trial import unittest

try:
    from autobahn.twisted.testing import create_memory_agent, MemoryReactorClockResolver, create_pumper
    HAVE_TESTING = True
except ImportError:
    HAVE_TESTING = False

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.websocket import WebSocketServerProtocol


class TestAgent(unittest.TestCase):

    skip = not HAVE_TESTING

    def setUp(self):
        self.pumper = create_pumper()
        self.reactor = MemoryReactorClockResolver()
        return self.pumper.start()

    def tearDown(self):
        return self.pumper.stop()

    @inlineCallbacks
    def test_echo_server(self):

        class EchoServer(WebSocketServerProtocol):
            def onMessage(self, msg, is_binary):
                self.sendMessage(msg)

        agent = create_memory_agent(self.reactor, self.pumper, EchoServer)
        proto = yield agent.open("ws://localhost:1234/ws", dict())

        messages = []

        def got(msg, is_binary):
            messages.append(msg)
        proto.on("message", got)

        proto.sendMessage(b"hello")

        if True:
            # clean close
            proto.sendClose()
        else:
            # unclean close
            proto.transport.loseConnection()
        yield proto.is_closed
        self.assertEqual([b"hello"], messages)

    @inlineCallbacks
    def test_secure_echo_server(self):

        class EchoServer(WebSocketServerProtocol):
            def onMessage(self, msg, is_binary):
                self.sendMessage(msg)

        agent = create_memory_agent(self.reactor, self.pumper, EchoServer)
        proto = yield agent.open("wss://localhost:1234/ws", dict())

        messages = []

        def got(msg, is_binary):
            messages.append(msg)
        proto.on("message", got)

        proto.sendMessage(b"hello")

        if True:
            # clean close
            proto.sendClose()
        else:
            # unclean close
            proto.transport.loseConnection()
        yield proto.is_closed
        self.assertEqual([b"hello"], messages)
