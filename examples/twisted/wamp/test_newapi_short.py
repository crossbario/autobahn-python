from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted import run

@coroutine
def on_join(session):
    # the session has joined the realm and the full range of
    # WAMP interactions are now possible
    try:
        res = yield session.call(u'com.example.add2', 2, 3)
        print("Result: {}".format(res))
    except Exception as e:
        print("Error: {}".format(e))
    finally:
        session.leave()

def main(connection):
    # this is hooking into a session event, but that is
    # replicated on as a connection event
    connection.on_join(on_join)

if __name__ == '__main__':
    # this is using the defaults: WAMP-over-WebSocket
    # to "ws://127.0.0.1:8080/ws" and realm "public"
    return run(main)
