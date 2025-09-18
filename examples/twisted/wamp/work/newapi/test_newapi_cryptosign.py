from autobahn.twisted.component import Component, run

privkey_hex = "6e3a302aa67d55ffc2059efeb5cf679470b37a26ae9ac18693b56ea3d0cd331c"
# pubkey: 020b13239ca0f10a1c65feaf26e8dfca6e84c81d2509a2b7b75a7e5ee5ce4b66


component = Component(
    transports="ws://localhost:8080/auth_ws",
    realm="crossbardemo",
    authentication={
        "cryptosign": {
            "authid": "alice",
            "privkey": privkey_hex,
        }
    },
)


@component.on_join
def join(session, details):
    print("Session {} joined: {}".format(details.session, details))


if __name__ == "__main__":
    run(component)
