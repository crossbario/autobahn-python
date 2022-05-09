from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError

# public-key-ed25519: 15cfa4acef5cc312e0b9ba77634849d0a8c6222a546f90eb5123667935d2f561
# private-key-ed25519: 20e8c05d0ede9506462bb049c4843032b18e8e75b314583d0c8d8a4942f9be40
# public-adr-eth: 0xe59C7418403CF1D973485B36660728a5f4A8fF9c
# private-key-eth: 6b08b6e186bd2a3b9b2f36e6ece3f8031fe788ab3dc4a1cfd3a489ea387c496b

PRINCIPALS = [
    {
        "authid": "client1@example.com",
        "realm": "realm1",
        "role": "user",
        "extra": {
            "foo": 23
        },
        "authorized_keys": [
            "15cfa4acef5cc312e0b9ba77634849d0a8c6222a546f90eb5123667935d2f561"
        ]
    }
]


class Authenticator(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):

        # build a map from pubkeys to principals
        pubkey_to_principals = {}
        for p in PRINCIPALS:
            for k in p['authorized_keys']:
                if k in pubkey_to_principals:
                    raise Exception("ambiguous key {}".format(k))
                else:
                    pubkey_to_principals[k] = p

        # this is our dynamic authenticator procedure that will be called by Crossbar.io
        # when a session is authenticating
        def authenticate(realm, authid, details):
            self.log.debug("authenticate({realm}, {authid}, {details})",
                           realm=realm, authid=authid, details=details)

            assert('authmethod' in details)
            assert(details['authmethod'] == 'cryptosign')
            assert('authextra' in details)
            assert('pubkey' in details['authextra'])

            pubkey = details['authextra']['pubkey']
            self.log.info(
                "authenticating session with public key = {pubkey}", pubkey=pubkey)

            if pubkey in pubkey_to_principals:
                principal = pubkey_to_principals[pubkey]
                auth = {
                    'pubkey': pubkey,
                    'realm': principal['realm'],
                    'authid': principal['authid'],
                    'role': principal['role'],
                    'extra': principal['extra'],
                    'cache': True
                }
                self.log.info(
                    "found valid principal {authid} matching public key", authid=auth['authid'])
                return auth
            else:
                msg = 'no principal with matching public key 0x{}'.format(pubkey)
                self.log.warn(msg)
                raise ApplicationError('com.example.no_such_user', msg)

        # register our dynamic authenticator with Crossbar.io
        try:
            yield self.register(authenticate, 'com.example.authenticate')
            self.log.info("Dynamic authenticator registered!")
        except Exception as e:
            self.log.info(
                "Failed to register dynamic authenticator: {0}".format(e))
