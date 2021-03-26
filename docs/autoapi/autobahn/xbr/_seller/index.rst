:mod:`autobahn.xbr._seller`
===========================

.. py:module:: autobahn.xbr._seller


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.xbr._seller.KeySeries
   autobahn.xbr._seller.PayingChannel
   autobahn.xbr._seller.SimpleSeller



.. class:: KeySeries(api_id, price, interval=None, count=None, on_rotate=None)


   Bases: :class:`object`

   Data encryption key series with automatic (time-based) key rotation
   and key offering (to the XBR market maker).

   .. method:: key_id(self)
      :property:

      Get current XBR data encryption key ID (of the keys being rotated
      in a series).

      :return: Current key ID in key series (16 bytes).
      :rtype: bytes


   .. method:: encrypt(self, payload)
      :async:

      Encrypt data with the current XBR data encryption key.

      :param payload: Application payload to encrypt.
      :type payload: object

      :return: The ciphertext for the encrypted application payload.
      :rtype: bytes


   .. method:: encrypt_key(self, key_id, buyer_pubkey)

      Encrypt a (previously used) XBR data encryption key with a buyer public key.

      :param key_id: ID of the data encryption key to encrypt.
      :type key_id: bytes

      :param buyer_pubkey: Buyer WAMP public key (Ed25519) to asymmetrically encrypt
          the data encryption key (selected by ``key_id``) against.
      :type buyer_pubkey: bytes

      :return: The ciphertext for the encrypted data encryption key.
      :rtype: bytes


   .. method:: start(self)
      :abstractmethod:


   .. method:: stop(self)
      :abstractmethod:


   .. method:: _rotate(self)
      :async:



.. class:: PayingChannel(adr, seq, balance)


   Bases: :class:`object`


.. class:: SimpleSeller(market_maker_adr, seller_key, provider_id=None)


   Bases: :class:`object`

   .. attribute:: log
      

      

   .. attribute:: KeySeries
      

      

   .. attribute:: STATE_NONE
      :annotation: = 0

      

   .. attribute:: STATE_STARTING
      :annotation: = 1

      

   .. attribute:: STATE_STARTED
      :annotation: = 2

      

   .. attribute:: STATE_STOPPING
      :annotation: = 3

      

   .. attribute:: STATE_STOPPED
      :annotation: = 4

      

   .. method:: public_key(self)
      :property:

      This seller delegate public Ethereum key.

      :return: Ethereum public key of this seller delegate.
      :rtype: bytes


   .. method:: add(self, api_id, prefix, price, interval=None, count=None, categories=None)

      Add a new (rotating) private encryption key for encrypting data on the given API.

      :param api_id: API for which to create a new series of rotating encryption keys.
      :type api_id: bytes

      :param price: Price in XBR token per key.
      :type price: int

      :param interval: Interval (in seconds) after which to auto-rotate the encryption key.
      :type interval: int

      :param count: Number of encryption operations after which to auto-rotate the encryption key.
      :type count: int


   .. method:: start(self, session)
      :async:

      Start rotating keys and placing key offers with the XBR market maker.

      :param session: WAMP session over which to communicate with the XBR market maker.
      :type session: :class:`autobahn.wamp.protocol.ApplicationSession`


   .. method:: stop(self)
      :async:

      Stop rotating/offering keys to the XBR market maker.


   .. method:: balance(self)
      :async:

      Return current (off-chain) balance of paying channel:

      * ``amount``: The initial amount with which the paying channel was opened.
      * ``remaining``: The remaining amount of XBR in the paying channel that can be earned.
      * ``inflight``: The amount of XBR allocated to sell transactions that are currently processed.

      :return: Current paying balance.
      :rtype: dict


   .. method:: wrap(self, api_id, uri, payload)
      :async:

      Encrypt and wrap application payload for a given API and destined for a specific WAMP URI.

      :param api_id: API for which to encrypt and wrap the application payload for.
      :type api_id: bytes

      :param uri: WAMP URI the application payload is destined for (eg the procedure or topic URI).
      :type uri: str

      :param payload: Application payload to encrypt and wrap.
      :type payload: object

      :return: The encrypted and wrapped application payload: a tuple with ``(key_id, serializer, ciphertext)``.
      :rtype: tuple


   .. method:: close_channel(self, market_maker_adr, channel_oid, channel_seq, channel_balance, channel_is_final, marketmaker_signature, details=None)

      Called by a XBR Market Maker to close a paying channel.


   .. method:: sell(self, market_maker_adr, buyer_pubkey, key_id, channel_oid, channel_seq, amount, balance, signature, details=None)

      Called by a XBR Market Maker to buy a data encyption key. The XBR Market Maker here is
      acting for (triggered by) the XBR buyer delegate.

      :param market_maker_adr: The market maker Ethereum address. The technical buyer is usually the
          XBR market maker (== the XBR delegate of the XBR market operator).
      :type market_maker_adr: bytes of length 20

      :param buyer_pubkey: The buyer delegate Ed25519 public key.
      :type buyer_pubkey: bytes of length 32

      :param key_id: The UUID of the data encryption key to buy.
      :type key_id: bytes of length 16

      :param channel_oid: The on-chain channel contract address.
      :type channel_oid: bytes of length 16

      :param channel_seq: Paying channel sequence off-chain transaction number.
      :type channel_seq: int

      :param amount: The amount paid by the XBR Buyer via the XBR Market Maker.
      :type amount: bytes

      :param balance: Balance remaining in the payment channel (from the market maker to the
          seller) after successfully buying the key.
      :type balance: bytes

      :param signature: Signature over the supplied buying information, using the Ethereum
          private key of the market maker (which is the delegate of the marker operator).
      :type signature: bytes of length 65

      :param details: Caller details. The call will come from the XBR Market Maker.
      :type details: :class:`autobahn.wamp.types.CallDetails`

      :return: The data encryption key, itself encrypted to the public key of the original buyer.
      :rtype: bytes



