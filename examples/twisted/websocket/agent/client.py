

from autobahn.twisted.websocket import create_client_agent
from twisted.internet import task


async def main(reactor):
    agent = create_client_agent(reactor)
    options = {
        "headers": {
            "x-foo": "bar",
        }
    }
    proto = await agent.open("ws://localhost:9000/ws", options)

    def stuff(*args, **kw):
        print("stuff: {} {}".format(args, kw))
    proto.on('message', stuff)

    proto.sendMessage(b"i am a message\n")
    await task.deferLater(reactor, 1.0, lambda: None)
    proto.sendMessage(b"i am a message\n")
    await task.deferLater(reactor, 1.0, lambda: None)
    proto.sendMessage(b"i am a message\n")
    await task.deferLater(reactor, 1.0, lambda: None)


    proto.transport.loseConnection()
    x = await proto.is_closed
    print("closed {}".format(x))


if __name__ == "__main__":
    from twisted.internet.defer import ensureDeferred
    task.react(lambda r: ensureDeferred(main(r)))
