
from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.testing import create_memory_agent

class TestAgent(unittest.TestCase):

    def setUp(self):
        pass

    @inlineCallbacks
    def test_foo(self):
        agent = create_memory_agent()
        proto = yield agent.open("ws://localhost:1234/ws", dict())

        proto.sendMessage(b"hello")
        agent.flush()
