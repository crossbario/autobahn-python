from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession


class MyAuthorizer(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
       print("MyAuthorizer.onJoin({})".format(details))
       try:
           yield self.register(self.authorize, u'com.example.authorize')
           print("MyAuthorizer: authorizer registered")
       except Exception as e:
           print("MyAuthorizer: failed to register authorizer procedure ({})".format(e))
           raise

    def authorize(self, details, uri, action, options):
        print("MyAuthorizer.authorize(uri='{}', action='{}', options='{}')".format(uri, action, options))
        print("options:")
        for k, v in options.items():
            print("  {}: {}".format(k, v))
        if False:
            print("I allow everything.")
        else:
            if uri == u'com.foo.private':
                return False
            if options.get(u"match", "exact") != u"exact":
                print("only exact-match subscriptions allowed")
                return False
        return True
