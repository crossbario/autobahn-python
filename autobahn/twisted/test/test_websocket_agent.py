
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
        self.reactor = MemoryReactorClockResolver()

    @inlineCallbacks
    def _test_foo(self):
        agent = create_memory_agent(self.reactor, SpammingWebSocketServerProtocol)
        proto = yield agent.open("ws://localhost:1234/ws", dict())

        proto.sendMessage(b"hello")
        agent.flush()

    @inlineCallbacks
    def test_echo_server(self):

        class EchoServer(WebSocketServerProtocol):
            def onOpen(self):
                print("open")
                print("sent",self.sendMessage(b"hello"))

            def onMesssage(self, msg, isBinary):
                print("gotmessage {}".format(msg))
                self.sendMessage(msg, isBinary=is_binary)

            def onClose(*args):
                print("close {}".format(args))

        agent = create_memory_agent(self.reactor, EchoServer)
        proto = yield agent.open("ws://localhost:1234/ws", dict())

        messages = []
        def got(msg, isBinary):
            print("got", msg)
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
