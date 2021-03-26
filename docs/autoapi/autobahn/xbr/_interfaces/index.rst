:mod:`autobahn.xbr._interfaces`
===============================

.. py:module:: autobahn.xbr._interfaces


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.xbr._interfaces.IMarketMaker
   autobahn.xbr._interfaces.IProvider
   autobahn.xbr._interfaces.IConsumer
   autobahn.xbr._interfaces.ISeller
   autobahn.xbr._interfaces.IBuyer
   autobahn.xbr._interfaces.IDelegate



.. class:: IMarketMaker

   Bases: :class:`abc.ABC`

   XBR Market Maker interface.

   .. method:: status(self, details)
      :abstractmethod:

      :param details:
      :return:


   .. method:: offer(self, key_id, price, details)
      :abstractmethod:

      :param key_id:
      :param price:
      :param details:
      :return:


   .. method:: revoke(self, key_id, details)
      :abstractmethod:

      :param key_id:
      :param details:
      :return:


   .. method:: quote(self, key_id, details)
      :abstractmethod:

      :param key_id:
      :param details:
      :return:


   .. method:: buy(self, channel_id, channel_seq, buyer_pubkey, datakey_id, amount, balance, signature, details)
      :abstractmethod:

      :param channel_id:
      :param channel_seq:
      :param buyer_pubkey:
      :param datakey_id:
      :param amount:
      :param balance:
      :param signature:
      :param details:
      :return:


   .. method:: get_payment_channels(self, address, details)
      :abstractmethod:

      :param address:
      :param details:
      :return:


   .. method:: get_payment_channel(self, channel_id, details)
      :abstractmethod:

      :param channel_id:
      :param details:
      :return:



.. class:: IProvider

   Bases: :class:`abc.ABC`

   XBR Provider interface.

   .. method:: sell(self, key_id, buyer_pubkey, amount_paid, post_balance, signature, details)
      :abstractmethod:

      :param key_id:
      :param buyer_pubkey:
      :param amount_paid:
      :param post_balance:
      :param signature:
      :param details:
      :return:



.. class:: IConsumer

   Bases: :class:`abc.ABC`

   XBR Consumer interface.


.. class:: ISeller

   Bases: :class:`abc.ABC`

   XBR Seller interface.

   .. method:: start(self, session)
      :abstractmethod:
      :async:

      :param session:
      :return:


   .. method:: wrap(self, uri, payload)
      :abstractmethod:
      :async:

      :param uri:
      :param payload:
      :return:



.. class:: IBuyer

   Bases: :class:`abc.ABC`

   XBR Buyer interface.

   .. method:: start(self, session)
      :abstractmethod:
      :async:

      Start buying keys over the provided session.

      :param session: WAMP session that allows to talk to the XBR Market Maker.


   .. method:: unwrap(self, key_id, enc_ser, ciphertext)
      :abstractmethod:
      :async:

      Decrypt and deserialize received XBR payload.

      :param key_id: The ID of the datakey the payload is encrypted with.
      :type key_id: bytes

      :param enc_ser: The serializer that was used for serializing the payload. One of ``cbor``, ``json``, ``msgpack``, ``ubjson``.
      :type enc_ser: str

      :param ciphertext: The encrypted payload to unwrap.
      :type ciphertext: bytes

      :returns: The unwrapped application payload.
      :rtype: object



.. class:: IDelegate

   Bases: :class:`autobahn.xbr._interfaces.ISeller`, :class:`autobahn.xbr._interfaces.IBuyer`

   XBR Delegate interface.


