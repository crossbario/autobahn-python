from autobahn.twisted.component import Component, run

# or: from autobahn.asyncio.component import Component, run
from twisted.internet.defer import inlineCallbacks

demo = Component(
    transports=[
        {
            "url": "wss://demo.crossbar.io/ws",
        }
    ],
    realm="crossbardemo",
)


# 1. subscribe to a topic
@demo.subscribe("io.crossbar.demo.hello")
def hello(msg):
    print("Got hello: {}".format(msg))


# 2. register a procedure for remote calling
@demo.register("io.crossbar.demo.add2")
def add2(x, y):
    return x + y


# 3. after we've authenticated, run some code
@demo.on_join
async def joined(session, details):
    # publish an event (won't go to "this" session by default)
    session.publish("io.crossbar.demo.hello", "Hello, world!")

    # 4. call a remote procedure
    result = await session.call("io.crossbar.demo.add2", 2, 3)
    print("io.crossbar.demo.add2(2, 3) = {}".format(result))

    await session.leave()


if __name__ == "__main__":
    run([demo])
