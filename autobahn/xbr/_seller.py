###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import os
import uuid
import binascii

import cbor2
import nacl.secret
import nacl.utils

from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall

import txaio

from zlmdb import time_ns

from autobahn.wamp.types import RegisterOptions
from autobahn.wamp.exception import ApplicationError, TransportLost
from autobahn.twisted.util import sleep
from autobahn.wamp.types import CallDetails

from autobahn import xbr

import eth_keys
from eth_account import Account

from ._interfaces import IProvider, ISeller
from ._util import hl


class KeySeries(object):

    log = txaio.make_logger()

    def __init__(self, api_id, price, interval, on_rotate=None):
        assert type(api_id) == bytes and len(api_id) == 16
        assert type(price) == int and price > 0
        assert type(interval) == int and interval > 0

        self._api_id = api_id
        self._price = price
        self._interval = interval
        self._on_rotate = on_rotate

        self._id = None
        self._key = None
        self._box = None
        self._archive = {}

        self._run_loop = None
        self._started = None

    @property
    def key_id(self):
        """
        Get current XBR data encryption key ID.

        :return:
        """
        return self._id

    def encrypt(self, payload):
        """
        Encrypt data with the current XBR data encryption key.

        :param payload:
        :return:
        """
        data = cbor2.dumps(payload)
        ciphertext = self._box.encrypt(data)

        return self._id, 'cbor', ciphertext

    def encrypt_key(self, key_id, buyer_pubkey):
        """
        Encrypt a previously used XBR data encryption key with a buyer public key.

        :param key_id:
        :param buyer_pubkey:
        :return:
        """

        # FIXME: check amount paid, post balance and signature
        # FIXME: sign transaction
        key, _ = self._archive[key_id]

        sendkey_box = nacl.public.SealedBox(nacl.public.PublicKey(buyer_pubkey,
                                                                  encoder=nacl.encoding.RawEncoder))

        encrypted_key = sendkey_box.encrypt(key, encoder=nacl.encoding.RawEncoder)

        return encrypted_key

    def start(self):
        assert self._run_loop is None

        self.log.info('Starting key rotation every {interval} seconds for api_id="{api_id}" ..',
                      interval=hl(self._interval), api_id=hl(uuid.UUID(bytes=self._api_id)))

        self._run_loop = LoopingCall(self._rotate)
        self._started = self._run_loop.start(self._interval)

        return self._started

    def stop(self):
        assert self._run_loop

        if self._run_loop:
            self._run_loop.stop()
            self._run_loop = None

        return self._started

    @inlineCallbacks
    def _rotate(self):
        self._id = os.urandom(16)
        self._key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
        self._box = nacl.secret.SecretBox(self._key)

        self._archive[self._id] = (self._key, self._box)

        self.log.info(
            '{tx_type} key "{key_id}" rotated [api_id="{api_id}"]',
            tx_type=hl('XBR ROTATE', color='magenta'),
            key_id=hl(uuid.UUID(bytes=self._id)),
            api_id=hl(uuid.UUID(bytes=self._api_id)))

        if self._on_rotate:
            yield self._on_rotate(self)


class SimpleSeller(object):

    log = txaio.make_logger()

    def __init__(self, market_maker_adr, seller_key, provider_id=None):
        """

        :param market_maker_adr:
        :type market_maker_adr:

        :param seller_key:
        :type seller_key:

        :param provider_id:
        :type provider_id:
        """
        assert type(market_maker_adr) == bytes and len(market_maker_adr) == 20, 'market_maker_adr must be bytes[20], but got "{}"'.format(market_maker_adr)
        assert type(seller_key) == bytes and len(seller_key) == 32, 'seller delegate must be bytes[32], but got "{}"'.format(seller_key)
        assert provider_id is None or type(provider_id) == str, 'provider_id must be None or string, but got "{}"'.format(provider_id)

        self._market_maker_adr = market_maker_adr

        # seller private key/account
        self._pkey = eth_keys.keys.PrivateKey(seller_key)
        self._acct = Account.privateKeyToAccount(self._pkey)
        self._addr = self._pkey.public_key.to_canonical_address()

        self._provider_id = provider_id or str(self._pkey.public_key)

        self._keys = {}
        self._keys_map = {}

        # after start() is running, these will be set
        self._session = None
        self._session_regs = None

    @property
    def public_key(self):
        """
        Get the seller public key.

        :return:
        """
        return self._pkey.public_key

    def add(self, api_id, prefix, price, interval, categories=None):
        """
        Add a new (rotating) private encryption key for encrypting data on the given API.

        :param api_id: API for which to create a new series of rotating encryption keys.
        :param price: Price in XBR token per key.
        :param interval: Interval (in seconds) in which to auto-rotate the encryption key.
        """
        assert api_id not in self._keys

        @inlineCallbacks
        def on_rotate(key_series):

            key_id = key_series.key_id

            self._keys_map[key_id] = key_series

            # offer the key to the market maker (retry 5x in specific error cases)
            retries = 5
            while retries:
                try:
                    valid_from = time_ns() - 10 * 10 ** 9

                    delegate = self._addr

                    # FIXME: sign the supplied offer information using self._pkey
                    signature = os.urandom(64)

                    offer = yield self._session.call('xbr.marketmaker.place_offer',
                                                     key_id,
                                                     api_id,
                                                     prefix,
                                                     valid_from,
                                                     delegate,
                                                     signature,
                                                     privkey=None,
                                                     price=price,
                                                     categories=categories,
                                                     expires=None,
                                                     copies=None,
                                                     provider_id=self._provider_id)

                    self.log.info(
                        '{tx_type} key "{key_id}" offered for {price} [api_id={api_id}, prefix="{prefix}", delegate="{delegate}"]',
                        tx_type=hl('XBR OFFER ', color='magenta'),
                        key_id=hl(uuid.UUID(bytes=key_id)),
                        api_id=hl(uuid.UUID(bytes=api_id)),
                        price=hl(str(price) + ' XBR', color='magenta'),
                        delegate=hl(binascii.b2a_hex(delegate).decode()),
                        prefix=hl(prefix))

                    self.log.debug('offer={offer}', offer=offer)

                    break

                except ApplicationError as e:
                    if e.error == 'wamp.error.no_such_procedure':
                        self.log.warn('xbr.marketmaker.offer: procedure unavailable!')
                    else:
                        self.log.failure()
                        break
                except TransportLost:
                    self.log.warn('TransportLost while calling xbr.marketmaker.offer!')
                    break
                except:
                    self.log.failure()

                retries -= 1
                self.log.warn('Failed to place offer for key! Retrying {retries}/5 ..', retries=retries)
                yield sleep(1)

        key_series = KeySeries(api_id, price, interval, on_rotate)
        self._keys[api_id] = key_series

        return key_series

    @inlineCallbacks
    def start(self, session):
        """
        Start rotating keys and placing key offers with the XBR market maker.

        :param session: WAMP session over which to communicate with the XBR market maker.
        :param provider_id: The XBR provider ID.
        :return:
        """
        assert self._session is None

        self._session = session
        self._session_regs = []

        procedure = 'xbr.provider.{}.sell'.format(self._provider_id)
        reg = yield session.register(self.sell, procedure, options=RegisterOptions(details_arg='details'))
        self._session_regs.append(reg)
        self.log.info('Registered procedure "{procedure}"', procedure=hl(reg.procedure))

        for key_series in self._keys.values():
            key_series.start()

        if False:
            dl = []
            for func in [self.sell]:
                procedure = 'xbr.provider.{}.{}'.format(self._provider_id, func.__name__)
                d = session.register(func, procedure, options=RegisterOptions(details_arg='details'))
                dl.append(d)
            d = txaio.gather(dl)

            def registered(regs):
                for reg in regs:
                    self.log.info('Registered procedure "{procedure}"', procedure=hl(reg.procedure))
                self._session_regs = regs

            d.addCallback(registered)

            return d

    def stop(self):
        """

        :return:
        """
        dl = []
        for key_series in self._keys.values():
            d = key_series.stop()
            dl.append(d)

        if self._session_regs:
            if self._session and self._session.is_attached():
                # voluntarily unregister interface
                for reg in self._session_regs:
                    d = reg.unregister()
                    dl.append(d)
            self._session_regs = None

        d = txaio.gather(dl)
        return d

    async def wrap(self, api_id, uri, payload):
        """

        :param uri:
        :param payload:
        :return:
        """
        assert api_id in self._keys
        assert type(uri) == str
        assert payload is not None

        keyseries = self._keys[api_id]

        key_id, serializer, ciphertext = keyseries.encrypt(payload)

        return key_id, serializer, ciphertext

    def sell(self, delegate_adr, buyer_pubkey, key_id, amount, balance, signature, details=None):
        """
        Called by a XBR Market Maker to buy a key, acting for (triggered by) the XBR buyer delegate.

        :param delegate_adr: The market maker Ethereum address. The technical buyer is usually the
            XBR market maker (== the XBR delegate of the XBR market operator).
        :type delegate_adr: bytes of length 20

        :param buyer_pubkey: The buyer delegate Ed25519 public key.
        :type buyer_pubkey: bytes of length 32

        :param key_id: The UUID of the data encryption key to buy.
        :type key_id: bytes of length 16

        :param amount:
        :type amount:

        :param balance: Balance remaining in the payment channel (from the market maker to the
            seller) after successfully buying the key.
        :type balance: int

        :param signature: Signature over the supplied buying information, using the Ethereum
            private key of the market maker (which is the delegate of the marker operator).
        :type signature: bytes

        :param details: Caller details. The call will come from the XBR Market Maker.
        :param details:

        :return: The data encryption key, itself encrypted to the public key of the original buyer.
        :rtype: bytes
        """
        assert type(delegate_adr) == bytes and len(delegate_adr) == 20, 'delegate_adr must be bytes[20]'
        assert type(buyer_pubkey) == bytes and len(buyer_pubkey) == 32, 'buyer_pubkey must be bytes[32]'
        assert type(key_id) == bytes and len(key_id) == 16, 'key_id must be bytes[16]'
        assert type(amount) == int, 'amount_paid must be int'
        assert type(balance) == int, 'post_balance must be int'
        assert type(signature) == bytes and len(signature) == (32 + 32 + 1), 'signature must be bytes[65]'
        assert details is None or isinstance(details, CallDetails), 'details must be autobahn.wamp.types.CallDetails'

        # check that the delegate_adr fits what we expect for the market maker
        if delegate_adr != self._market_maker_adr:
            raise ApplicationError('xbr.error.unexpected_delegate_adr',
                                   'unexpected market maker (delegate) address: expected 0x{}, but got 0x{}'.format(binascii.b2a_hex(self._market_maker_adr).decode(), binascii.b2a_hex(delegate_adr).decode()))

        # check the signature (over all input data for the buying of the key)
        signer_address = xbr.recover_eip712_signer(delegate_adr, buyer_pubkey, key_id, amount, balance, signature)
        if signer_address != delegate_adr:
            self.log.warn('EIP712 signature invalid: signer_address={signer_address}, delegate_adr={delegate_adr}',
                          signer_address=hl(binascii.b2a_hex(signer_address).decode()),
                          delegate_adr=hl(binascii.b2a_hex(delegate_adr).decode()))
            raise ApplicationError('xbr.error.invalid_signature', 'EIP712 signature invalid or not signed by market maker')

        # get the key series given the key_id
        if key_id not in self._keys_map:
            raise ApplicationError('crossbar.error.no_such_object', 'no key with ID "{}"'.format(key_id))
        key_series = self._keys_map[key_id]

        # encrypt the data encryption key against the original buyer delegate Ed25519 public key
        sealed_key = key_series.encrypt_key(key_id, buyer_pubkey)

        assert type(sealed_key) == bytes and len(sealed_key) == 80, 'unexpected sealed key computed (expected bytes[80]): {}'.format(sealed_key)

        self.log.info('{tx_type} key "{key_id}" sold for {amount_earned} [caller={caller}, caller_authid="{caller_authid}", buyer_pubkey="{buyer_pubkey}"]',
                      tx_type=hl('XBR SELL  ', color='magenta'),
                      key_id=hl(uuid.UUID(bytes=key_id)),
                      amount_earned=hl(str(amount) + ' XBR', color='magenta'),
                      # paying_channel=hl(binascii.b2a_hex(paying_channel).decode()),
                      caller=hl(details.caller),
                      caller_authid=hl(details.caller_authid),
                      buyer_pubkey=hl(binascii.b2a_hex(buyer_pubkey).decode()))

        return sealed_key


ISeller.register(SimpleSeller)
IProvider.register(SimpleSeller)
