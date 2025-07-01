from autobahn.twisted.websocket import create_client_agent
from twisted.internet import task


async def main(reactor):
    """
    Using the 'agent' interface to talk to the echo server (run
    ../echo/server.py for the server, for example)
    """
    agent = create_client_agent(reactor)
    options = {
        "headers": {
            "x-foo": "bar",
        }
    }
    proto = await agent.open("ws://localhost:9000/ws", options)

    def got_message(*args, **kw):
        print("on_message: args={} kwargs={}".format(args, kw))

    proto.on("message", got_message)

    await proto.is_open

    proto.sendMessage(b"i am a message\n")
    await task.deferLater(reactor, 0, lambda: None)

    proto.sendClose(code=1000, reason="byebye")

    await proto.is_closed


if __name__ == "__main__":
    from twisted.internet.defer import ensureDeferred

    task.react(lambda r: ensureDeferred(main(r)))
