
from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.testing import create_memory_agent
from autobahn.twisted.websocket import WebSocketServerProtocol


class SpammingWebSocketServerProtocol(WebSocketServerProtocol):
    def onMessage(self, *args, **kw):
        print("SERVER MESSAGE: {} {}".format(args, kw))


class TestAgent(unittest.TestCase):

    def setUp(self):
        pass

    @inlineCallbacks
    def test_foo(self):
        agent = create_memory_agent(SpammingWebSocketServerProtocol)
        proto = yield agent.open("ws://localhost:1234/ws", dict())

        proto.sendMessage(b"hello")
        agent.flush()
