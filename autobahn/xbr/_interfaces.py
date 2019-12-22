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

import abc


class IMarketMaker(abc.ABC):
    """
    XBR Market Maker interface.
    """

    @abc.abstractmethod
    def status(self, details):
        """

        :param details:
        :return:
        """

    @abc.abstractmethod
    def offer(self, key_id, price, details):
        """

        :param key_id:
        :param price:
        :param details:
        :return:
        """

    @abc.abstractmethod
    def revoke(self, key_id, details):
        """

        :param key_id:
        :param details:
        :return:
        """

    @abc.abstractmethod
    def quote(self, key_id, details):
        """

        :param key_id:
        :param details:
        :return:
        """

    @abc.abstractmethod
    def buy(self, channel_id, channel_seq, buyer_pubkey, datakey_id, amount, balance, signature, details):
        """

        :param channel_id:
        :param channel_seq:
        :param buyer_pubkey:
        :param datakey_id:
        :param amount:
        :param balance:
        :param signature:
        :param details:
        :return:
        """

    @abc.abstractmethod
    def get_payment_channels(self, address, details):
        """

        :param address:
        :param details:
        :return:
        """

    @abc.abstractmethod
    def get_payment_channel(self, channel_id, details):
        """

        :param channel_id:
        :param details:
        :return:
        """


class IProvider(abc.ABC):
    """
    XBR Provider interface.
    """

    @abc.abstractmethod
    def sell(self, key_id, buyer_pubkey, amount_paid, post_balance, signature, details):
        """

        :param key_id:
        :param buyer_pubkey:
        :param amount_paid:
        :param post_balance:
        :param signature:
        :param details:
        :return:
        """


class IConsumer(abc.ABC):
    """
    XBR Consumer interface.
    """


class ISeller(abc.ABC):
    """
    XBR Seller interface.
    """

    @abc.abstractmethod
    async def start(self, session):
        """

        :param session:
        :return:
        """

    @abc.abstractmethod
    async def wrap(self, uri, payload):
        """

        :param uri:
        :param payload:
        :return:
        """


class IBuyer(abc.ABC):
    """
    XBR Buyer interface.
    """

    @abc.abstractmethod
    async def start(self, session):
        """
        Start buying keys over the provided session.

        :param session: WAMP session that allows to talk to the XBR Market Maker.
        """

    @abc.abstractmethod
    async def unwrap(self, key_id, enc_ser, ciphertext):
        """
        Decrypt and deserialize received XBR payload.

        :param key_id: The ID of the datakey the payload is encrypted with.
        :type key_id: bytes

        :param enc_ser: The serializer that was used for serializing the payload. One of ``cbor``, ``json``, ``msgpack``, ``ubjson``.
        :type enc_ser: str

        :param ciphertext: The encrypted payload to unwrap.
        :type ciphertext: bytes

        :returns: The unwrapped application payload.
        :rtype: object
        """
