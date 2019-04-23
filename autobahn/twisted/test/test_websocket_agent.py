
from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks, Deferred
from autobahn.twisted.testing import create_memory_agent, MemoryReactorClockResolver
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketClientProtocol

from twisted.internet import reactor


class SpammingWebSocketServerProtocol(WebSocketServerProtocol):
    def onMessage(self, *args, **kw):
        print("SERVER MESSAGE: {} {}".format(args, kw))


class LoggingWebSocketServerProtocol(WebSocketServerProtocol):

    messages = []
    reactor = None

    def onOpen(self):
        # "break the loop" in synchonous agent behavior that means
        # we'll "do" all the message-sending before anything gets a
        # chance to listn ... but XXX THINK do we actually need to do
        # this "in autobahn" or is this a produce of "all in-memory
        # transports" which take zero time?
        def send_messages():
            for msg in self.messages:
                print("sending {}".format(msg))
                self.sendMessage(msg)
        self.reactor.callLater(0, send_messages)

    def onMessage(self, *args, **kw):
        print("SERVER GOT MESSAGE: {} {}".format(args, kw))


class TestAgent(unittest.TestCase):

    def setUp(self):
        pass

    @inlineCallbacks
    def test_foo(self):
        reactor = MemoryReactorClockResolver()
        agent = create_memory_agent(reactor, SpammingWebSocketServerProtocol, None)
        proto = yield agent.open("ws://localhost:1234/ws", dict())

        proto.sendMessage(b"hello")
        agent.flush()

    @inlineCallbacks
    def test_client_receives_two_messages_subclass(self):

        def make():
            p = LoggingWebSocketServerProtocol()
            p.reactor = agent._reactor
            p.messages = [
                b"message zero",
                b"message one",
            ]
            return p

        class Mine(WebSocketClientProtocol):
            messages = []

            def onMessage(self, *args, **kw):
                self.messages.append((args, kw))

        reactor = MemoryReactorClockResolver()
        agent = create_memory_agent(reactor, None, make)
        proto = yield agent.open("ws://localhost:1234/ws", dict(), Mine)

        agent.flush()
        agent._reactor.advance(1)
        agent.flush()
        self.assertEqual(len(proto.messages), 2)

    @inlineCallbacks
    def test_client_receives_two_messages_listener(self):

        reactor = MemoryReactorClockResolver()
        agent = create_memory_agent(reactor, None, None)
        proto = yield agent.open("ws://localhost:1234/ws", dict())

        messages = []

        def got_message(*args, **kw):
            messages.append((args, kw))
        proto.on("message", got_message)

        agent.flush()

        agent.send_server_message_to_client(proto, b"message one")
        self.assertEqual(1, len(messages))
        agent.send_server_message_to_client(proto, b"message two")
        self.assertEqual(2, len(messages))
