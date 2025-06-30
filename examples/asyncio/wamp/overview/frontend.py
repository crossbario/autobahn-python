from os import environ

from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession


class Component(ApplicationSession):
    async def onJoin(self, details):
        # listening for the corresponding message from the "backend"
        # (any session that .publish()es to this topic).
        def onevent(msg):
            print("Got event: {}".format(msg))

        await self.subscribe(onevent, "com.myapp.hello")

        # call a remote procedure.
        res = await self.call("com.myapp.add2", 2, 3)
        print("Got result: {}".format(res))


if __name__ == "__main__":
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/ws"),
        "crossbardemo",
    )
    runner.run(Component)
