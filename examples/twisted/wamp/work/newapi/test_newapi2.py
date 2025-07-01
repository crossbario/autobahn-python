from autobahn.twisted.connection import Connection
from autobahn.twisted.wamp import Session
from twisted.internet.defer import inlineCallbacks as coroutine
from twisted.internet.task import react


class MySession(Session):
    @coroutine
    def on_join(self, details):
        print("on_join: {}".format(details))

        def add2(a, b):
            return a + b

        yield self.register(add2, "com.example.add2")

        try:
            res = yield self.call("com.example.add2", 2, 3)
            print("result: {}".format(res))
        except Exception as e:
            print("error: {}".format(e))
        finally:
            print("leaving ..")
            # self.leave()

    def on_leave(self, details):
        print("on_leave xx: {}".format(details))
        self.disconnect()

    def on_disconnect(self):
        print("on_disconnect")


if __name__ == "__main__":
    transports = "ws://localhost:8080/ws"

    connection = Connection(transports=transports)
    connection.session = MySession
    react(connection.start)
