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

import uuid
import binascii

import os
import cbor2
import nacl.secret
import nacl.utils
import nacl.exceptions
import nacl.public

import txaio
from autobahn.twisted.util import sleep
from autobahn.wamp.exception import ApplicationError

import eth_keys
from eth_account import Account

from ._interfaces import IConsumer, IBuyer
from ._util import hl


class SimpleBuyer(object):
    """
    Simple XBR buyer component. This component can be used by a XBR consumer to handle
    XBR buying transactions to buy data keys for services used by the XBR consumer.

    on_offer_placed
    on_offer_revoked
    on_payment_channel_empty
    on_paying_channel_empty
    """

    log = txaio.make_logger()

    def __init__(self, buyer_key, max_price):
        """

        :param buyer_key: Consumer delegate (buyer) private Ethereum key.
        :type buyer_key: bytes
        """
        self._pkey = eth_keys.keys.PrivateKey(buyer_key)
        self._acct = Account.privateKeyToAccount(self._pkey)
        self._addr = self._pkey.public_key.to_canonical_address()

        self._max_price = max_price

        # this holds the keys we bought (map: key_id => nacl.secret.SecretBox)
        self._keys = {}
        self._session = None
        self._running = False

        self._receive_key = nacl.public.PrivateKey.generate()

    async def start(self, session, consumer_id):
        """
        Start buying keys to decrypt XBR data by calling ``unwrap()``.

        :param session:
        :param consumer_id:
        :return:
        """
        assert not self._running

        self._session = session
        self._running = True

        self.log.info('Start buying from consumer delegate address {address} (public key 0x{public_key}..)',
                      address=self._acct.address,
                      public_key=binascii.b2a_hex(self._pkey.public_key[:10]).decode())

        payment_channel = await session.call('xbr.marketmaker.get_payment_channel', self._addr)

        self.log.info('Delegate current payment channel: {payment_channel}',
                      payment_channel=hl(binascii.b2a_hex(payment_channel['channel']).decode()))

        if not payment_channel:
            raise Exception('no active payment channel found for delegate')
        if payment_channel['state'] != 1:
            raise Exception('payment channel not open')
        if payment_channel['remaining'] == 0:
            raise Exception('payment channel (amount={}) has no balance remaining'.format(payment_channel['remaining']))

        self._channel = payment_channel
        self._balance = payment_channel['remaining']

        return self._balance

    async def stop(self):
        assert self._running

        self._running = False

    async def balance(self):
        """
        Return current balance of payment channel:

        * ``amount``: The initial amount with which the payment channel was opened.
        * ``remaining``: The remaining amount of XBR in the payment channel that can be spent.
        * ``inflight``: The amount of XBR allocated to buy transactions that are currently processed.

        :return: Current payment balance.
        :rtype: dict
        """
        assert self._session and self._session.is_attached()

        payment_channel = await self._session.call('xbr.marketmaker.get_payment_channel', self._addr)

        if not payment_channel:
            raise Exception('no active payment channel found for delegate')
        if payment_channel['state'] != 1:
            raise Exception('payment channel not open')
        if payment_channel['remaining'] == 0:
            raise Exception('payment channel (amount={}) has no balance remaining'.format(payment_channel['remaining']))

        balance = {
            'amount': payment_channel['amount'],
            'remaining': payment_channel['remaining'],
            'inflight': payment_channel['inflight'],
        }

        return balance

    async def open_channel(self, buyer_addr, amount, details=None):
        """

        :param amount:
        :param details:
        :return:
        """
        assert self._session and self._session.is_attached()

        # FIXME
        signature = os.urandom(64)

        payment_channel = await self._session.call('xbr.marketmaker.open_payment_channel',
                                                   buyer_addr,
                                                   self._addr,
                                                   amount,
                                                   signature)

        balance = {
            'amount': payment_channel['amount'],
            'remaining': payment_channel['remaining'],
            'inflight': payment_channel['inflight'],
        }

        return balance

    async def close_channel(self, details=None):
        """
        Requests to close the currently active payment channel.

        :return:
        """

    async def unwrap(self, key_id, enc_ser, ciphertext):
        """
        Decrypt XBR data. This functions will potentially make the buyer call the
        XBR market maker to buy data encryption keys from the XBR provider.

        :param key_id:
        :param enc_ser:
        :param ciphertext:
        :return:
        """
        assert(enc_ser == 'cbor')

        # if we don't have the key, buy it!
        if key_id not in self._keys:
            # mark the key as currently being bought already (the location of code here is multi-entrant)
            self._keys[key_id] = False

            # call the market maker to buy the key
            amount = self._max_price

            # FIXME: compute actual kecchak256 based signature
            signature = b'\x00' * 64

            buyer_pubkey = self._receive_key.public_key.encode(encoder=nacl.encoding.RawEncoder)

            # call the market maker to buy the key
            #   -> channel_id, channel_seq, buyer_pubkey, datakey_id, amount, balance, signature
            try:
                receipt = await self._session.call('xbr.marketmaker.buy_key',
                                                   self._addr,
                                                   buyer_pubkey,
                                                   key_id,
                                                   amount,
                                                   signature)
            except Exception as e:
                self._keys[key_id] = e
                raise e

            sealed_key = receipt['sealed_key']

            unseal_box = nacl.public.SealedBox(self._receive_key)
            try:
                key = unseal_box.decrypt(sealed_key)
            except nacl.exceptions.CryptoError as e:
                self._keys[key_id] = e
                raise ApplicationError('xbr.error.decryption_failed', 'could not unseal data encryption key: {}'.format(e))

            # remember the key, so we can use it to actually decrypt application payload data
            self._keys[key_id] = nacl.secret.SecretBox(key)

            self.log.info(
                '{tx_type} key "{key_id}" bought for {amount_paid} [payment_channel="{payment_channel}", remaining={remaining}, inflight={inflight}, buyer_pubkey="{buyer_pubkey}"]',
                tx_type=hl('XBR BUY   ', color='magenta'),
                key_id=hl(uuid.UUID(bytes=key_id)),
                amount_paid=hl(str(receipt['amount_paid']) + ' XBR', color='magenta'),
                payment_channel=hl(binascii.b2a_hex(receipt['payment_channel']).decode()),
                remaining=hl(receipt['remaining']),
                inflight=hl(receipt['inflight']),
                buyer_pubkey=hl(binascii.b2a_hex(buyer_pubkey).decode()))

        # if the key is already being bought, wait until the one buying path of execution has succeeded and done
        log_counter = 0
        while self._keys[key_id] is False:
            if log_counter % 100:
                self.log.info('Waiting for key "{key_id}" currently being bought ..', key_id=hl(uuid.UUID(bytes=key_id)))
                log_counter += 1
            await sleep(.2)

        # check if the key buying failed and fail the unwrapping in turn
        if isinstance(self._keys[key_id], Exception):
            e = self._keys[key_id]
            raise e

        # now that we have the secret key, decrypt the event application payload
        try:
            message = self._keys[key_id].decrypt(ciphertext)
        except nacl.exceptions.CryptoError as e:
            # Decryption failed. Ciphertext failed verification
            raise ApplicationError('xbr.error.decryption_failed', 'failed to unwrap encrypted data: {}'.format(e))

        try:
            payload = cbor2.loads(message)
        except cbor2.decoder.CBORDecodeError as e:
            # premature end of stream (expected to read 4187 bytes, got 27 instead)
            raise ApplicationError('xbr.error.deserialization_failed', 'failed to deserialize application payload: {}'.format(e))

        return payload


IBuyer.register(SimpleBuyer)
IConsumer.register(SimpleBuyer)
