from autobahn.twisted.component import Component, run
from autobahn.wamp.types import RegisterOptions
from autobahn.wamp.exception import ApplicationError
from twisted.internet.defer import inlineCallbacks


component = Component(
    transports="ws://localhost:8080/auth_ws",
    realm="crossbardemo",
    authentication={
        "scram": {
            "authid": "carol",
            "authrole": "authenticated",
            "password": "p4ssw0rd",
            "kdf": "argon2id13",
        }
    },
)


@component.on_join
def joined(session, details):
    print("Session joined: {}".format(details))


if __name__ == "__main__":
    run([component])  # , log_level='debug')
