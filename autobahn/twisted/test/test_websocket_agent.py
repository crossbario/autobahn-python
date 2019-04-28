
from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.testing import create_memory_agent, MemoryReactorClockResolver, create_pumper
from autobahn.twisted.websocket import WebSocketServerProtocol


class TestAgent(unittest.TestCase):

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
