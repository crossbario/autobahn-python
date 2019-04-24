
from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks, Deferred
from autobahn.twisted.testing import create_memory_agent, MemoryReactorClockResolver
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketClientProtocol

from twisted.internet import reactor


class TestAgent(unittest.TestCase):

    def setUp(self):
        self.reactor = MemoryReactorClockResolver()

    @inlineCallbacks
    def test_echo_server(self):

        class EchoServer(WebSocketServerProtocol):
            def onMessage(self, msg, is_binary):
                self.sendMessage(msg)

        agent = create_memory_agent(self.reactor, EchoServer)
        proto = yield agent.open("ws://localhost:1234/ws", dict())

        messages = []
        def got(msg, is_binary):
            messages.append(msg)
        proto.on("message", got)

        proto.sendMessage(b"hello")
        agent.flush()

        if True:
            # clean close
            proto.sendClose()
        else:
            # unclean close
            proto.transport.loseConnection()
        agent.flush()
        yield proto.is_closed
        self.assertEqual([b"hello"], messages)
