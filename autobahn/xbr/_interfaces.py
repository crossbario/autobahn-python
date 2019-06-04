###############################################################################
#
# Copyright (c) Crossbar.io Technologies GmbH and contributors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.
#
###############################################################################

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class IMarketMaker(object):
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


@six.add_metaclass(abc.ABCMeta)
class IProvider(object):
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


@six.add_metaclass(abc.ABCMeta)
class IConsumer(object):
    """
    XBR Consumer interface.
    """


@six.add_metaclass(abc.ABCMeta)
class ISeller(object):
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


@six.add_metaclass(abc.ABCMeta)
class IBuyer(object):
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
