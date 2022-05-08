from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError


PRINCIPALS = [
    {
        "authid": "client01@example.com",
        "realm": "devices",
        "role": "device",
        "extra": {
            "foo": 23
        },
        "authorized_keys": [
            "545efb0a2192db8d43f118e9bf9aee081466e1ef36c708b96ee6f62dddad9122"
        ]
    },
    {
        "authid": "client02@example.com",
        "realm": "devices",
        "role": "device",
        "extra": {
            "foo": 42,
            "bar": "baz"
        },
        "authorized_keys": [
            "9c194391af3bf566fc11a619e8df200ba02efb35b91bdd98b424f20f4163875e",
            "585df51991780ee8dce4766324058a04ecae429dffd786ee80839c9467468c28"
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
