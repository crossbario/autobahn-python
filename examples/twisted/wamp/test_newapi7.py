# use newapi with Twisted's service.Service/Application API

from __future__ import print_function

import hmac
import hashlib
import unittest
from os import urandom
from base64 import b64encode

from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.application import service

from autobahn.twisted.connection import Connection
from autobahn.twisted.util import sleep
from autobahn.wamp.exception import ApplicationError


# could be an AB-provided helper?
def register_object(session, prefix, obj):
    """
    yield register_object(session, u"com.example.datetime.", datetime.datetime)
    """
    methods = [f for f in dir(obj) if not f.startswith('_')]
    print("registering", methods, "of", obj.__class__.__name__)

    return DeferredList(
        [session.register(getattr(obj, m), prefix + m) for m in methods]
    )


class UserSignUp(object):
    def __init__(self):
        self._private_key = b'123456789012345678901234567890AA'
        self._pending_users = dict()
        self._users = dict()

    def new_user(self, name, email):
        if name in self._users:
            raise ApplicationError("com.example.invalid_token", "Invalid user")

        nonce = urandom(32)
        sig = hmac.new(self._private_key, nonce, hashlib.sha256).digest()
        self._pending_users[nonce] = (name, email, sig)
        return nonce

    def redeem_token(self, token):
        alleged_sig = hmac.new(self._private_key, token, hashlib.sha256).digest()
        (name, email, sig) = self._pending_users.get(token, (None, None, None))
        if sig != alleged_sig:
            raise ApplicationError(u"com.example.invalid_token", u"Token is not valid")
        self._users[name] = (name, email,)
        return name

    def get_email(self, name):
        return self._users[name][1]

class TestUserSignUp(unittest.TestCase):
    def setUp(self):
        self.users = UserSignUp()

    def test_token_happy(self):
        token = self.users.new_user('meejah', 'meejah@meejah.ca')
        name = self.users.redeem_token(token)
        self.assertEqual(name, 'meejah')

    def test_token_sad(self):
        token = self.users.new_user('meejah', 'meejah@meejah.ca')
        self.assertRaises(Exception, self.users.redeem_token, b'0'*32)


class ApiService(service.Service):
    name = 'create_users'

    def startService(self):
        self._users_api = UserSignUp()
        self._session = None
        self._connection = Connection(
            transports=u'ws://127.0.0.1:8080/ws',
            main=self._start_session,
        )
        self._connection.start()

    @inlineCallbacks
    def stopService(self):
        print("stop service", self._session)
        if self._session:
            yield sleep(1)
            yield self._session.leave()
            yield self._session.disconnect()

    @inlineCallbacks
    def _start_session(self, reactor, session):
        self._session = session
        yield session.join(u'crossbardemo')
        yield register_object(session, u"com.example.users.", self._users_api)
        print("API active at com.example.users.*")

        print("self-test:")
        token = yield session.call(u"com.example.users.new_user", "foo", "foo@example.com")
        print(" created token:", b64encode(token))
        user = yield session.call(u"com.example.users.redeem_token", token)
        print(" redeemed for user:", user)
        email = yield session.call(u"com.example.users.get_email", user)
        print(" got email address:", email)


# run this with "twistd -noy test_newapi7.py". the "application"
# variable is a magic thing for twistd.
application = service.Application("create users WAMP API")
ApiService().setServiceParent(application)
