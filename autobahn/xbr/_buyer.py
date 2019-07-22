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
from autobahn.wamp.protocol import ApplicationSession

import web3
import eth_keys
from eth_account import Account

from ._interfaces import IConsumer, IBuyer
from ._util import hl, sign_eip712_data, recover_eip712_signer


class SimpleBuyer(object):
    """
    Simple XBR buyer component. This component can be used by a XBR buyer delegate to
    handle the automated buying of data encryption keys from the XBR market maker.
    """

    log = txaio.make_logger()

    def __init__(self, market_maker_adr, buyer_key, max_price):
        """

        :param market_maker_adr:
        :type market_maker_adr:

        :param buyer_key: Consumer delegate (buyer) private Ethereum key.
        :type buyer_key: bytes

        :param max_price: Maximum price we are willing to buy per key.
        :type max_price: int
        """
        assert type(market_maker_adr) == bytes and len(market_maker_adr) == 20, 'market_maker_adr must be bytes[20], but got "{}"'.format(market_maker_adr)
        assert type(buyer_key) == bytes and len(buyer_key) == 32, 'buyer delegate must be bytes[32], but got "{}"'.format(buyer_key)
        assert type(max_price) == int and max_price > 0

        # market maker address
        self._market_maker_adr = market_maker_adr

        # buyer raw ethereum private key (32 bytes)
        self._pkey_raw = buyer_key

        # buyer ethereum private key object
        self._pkey = eth_keys.keys.PrivateKey(buyer_key)

        # buyer ethereum private account from raw private key
        self._acct = Account.privateKeyToAccount(self._pkey)

        # buyer ethereum account canonical address
        self._addr = self._pkey.public_key.to_canonical_address()

        # buyer ethereum account canonical checksummed address
        self._caddr = web3.Web3.toChecksumAddress(self._addr)

        # maximum price per key we are willing to pay
        self._max_price = max_price

        # this holds the keys we bought (map: key_id => nacl.secret.SecretBox)
        self._keys = {}
        self._session = None
        self._running = False

        self._receive_key = nacl.public.PrivateKey.generate()

    async def start(self, session, consumer_id):
        """
        Start buying keys to decrypt XBR data by calling ``unwrap()``.

        :param session: WAMP session over which to communicate with the XBR market maker.
        :type session: :class:`autobahn.wamp.protocol.ApplicationSession`

        :param consumer_id: XBR consumer ID.
        :type consumer_id: str

        :return: Current remaining balance in payment channel.
        :rtype: int
        """
        assert isinstance(session, ApplicationSession)
        assert type(consumer_id) == str
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
        self._balance = payment_channel['amount']

        return self._balance

    async def stop(self):
        """
        Stop buying keys.
        """
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
        :type amount:

        :param details:
        :type details:

        :return:
        :rtype:
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

    async def unwrap(self, key_id, serializer, ciphertext):
        """
        Decrypt XBR data. This functions will potentially make the buyer call the
        XBR market maker to buy data encryption keys from the XBR provider.

        :param key_id: ID of the data encryption used for decryption
            of application payload.
        :type key_id: bytes

        :param serializer: Application payload serializer.
        :type serializer: str

        :param ciphertext: Ciphertext of encrypted application payload to
            decrypt.
        :type ciphertext: bytes

        :return: Decrypted application payload.
        :rtype: object
        """
        assert type(key_id) == bytes and len(key_id) == 16
        # FIXME: support more app payload serializers
        assert type(serializer) == str and serializer == 'cbor'
        assert type(ciphertext) == bytes

        # if we don't have the key, buy it!
        if key_id not in self._keys:
            # mark the key as currently being bought already (the location of code here is multi-entrant)
            self._keys[key_id] = False

            # get (current) price for key we want to buy
            quote = await self._session.call('xbr.marketmaker.get_quote', key_id)

            if quote['price'] > self._max_price:
                raise ApplicationError('xbr.error.max_price_exceeded',
                                       'key {} needed cannot be bought: price {} exceeds maximum price of {}'.format(uuid.UUID(bytes=key_id), quote['price'], self._max_price))

            # set price we pay set to the (current) quoted price
            amount = quote['price']

            # FIXME
            channel_seq = 1

            # check (locally) we have enough balance left in the payment channel to buy the key
            balance = self._balance - amount
            if balance < 0:
                raise ApplicationError('xbr.error.insufficient_balance',
                                       'key {} needed cannot be bought: insufficient balance {} in payment channel for amount {}'.format(uuid.UUID(bytes=key_id), self._balance, amount))

            buyer_pubkey = self._receive_key.public_key.encode(encoder=nacl.encoding.RawEncoder)

            # XBRSIG[1/8]: compute EIP712 typed data signature
            signature = sign_eip712_data(self._pkey_raw, buyer_pubkey, key_id, channel_seq, amount, balance)

            # call the market maker to buy the key
            try:
                receipt = await self._session.call('xbr.marketmaker.buy_key',
                                                   self._addr,
                                                   buyer_pubkey,
                                                   key_id,
                                                   channel_seq,
                                                   amount,
                                                   balance,
                                                   signature)
            except Exception as e:
                self._keys[key_id] = e
                raise e
            else:
                self._balance -= amount

            # XBRSIG[8/8]: check market maker signature
            marketmaker_signature = receipt['signature']
            signer_address = recover_eip712_signer(self._market_maker_adr, buyer_pubkey, key_id, channel_seq, amount, balance, marketmaker_signature)
            if signer_address != self._market_maker_adr:
                self.log.warn('EIP712 signature invalid: signer_address={signer_address}, delegate_adr={delegate_adr}',
                              signer_address=hl(binascii.b2a_hex(signer_address).decode()),
                              delegate_adr=hl(binascii.b2a_hex(self._market_maker_adr).decode()))
                raise ApplicationError('xbr.error.invalid_signature',
                                       'EIP712 signature invalid or not signed by market maker')

            # unseal the data encryption key
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

        # now that we have the data encryption key, decrypt the application payload
        try:
            message = self._keys[key_id].decrypt(ciphertext)
        except nacl.exceptions.CryptoError as e:
            # Decryption failed. Ciphertext failed verification
            raise ApplicationError('xbr.error.decryption_failed', 'failed to unwrap encrypted data: {}'.format(e))

        # deserialize the application payload
        # FIXME: support more app payload serializers
        try:
            payload = cbor2.loads(message)
        except cbor2.decoder.CBORDecodeError as e:
            # premature end of stream (expected to read 4187 bytes, got 27 instead)
            raise ApplicationError('xbr.error.deserialization_failed', 'failed to deserialize application payload: {}'.format(e))

        return payload


IBuyer.register(SimpleBuyer)
IConsumer.register(SimpleBuyer)
