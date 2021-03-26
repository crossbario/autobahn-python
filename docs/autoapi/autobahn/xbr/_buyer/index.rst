:mod:`autobahn.xbr._buyer`
==========================

.. py:module:: autobahn.xbr._buyer


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.xbr._buyer.Transaction
   autobahn.xbr._buyer.SimpleBuyer



.. class:: Transaction(channel, delegate, pubkey, key_id, channel_seq, amount, balance, signature)


   Bases: :class:`object`

   .. method:: marshal(self)


   .. method:: __str__(self)

      Return str(self).



.. class:: SimpleBuyer(market_maker_adr, buyer_key, max_price)


   Bases: :class:`object`

   Simple XBR buyer component. This component can be used by a XBR buyer delegate to
   handle the automated buying of data encryption keys from the XBR market maker.

   .. attribute:: log
      

      

   .. method:: start(self, session, consumer_id)
      :async:

      Start buying keys to decrypt XBR data by calling ``unwrap()``.

      :param session: WAMP session over which to communicate with the XBR market maker.
      :type session: :class:`autobahn.wamp.protocol.ApplicationSession`

      :param consumer_id: XBR consumer ID.
      :type consumer_id: str

      :return: Current remaining balance in payment channel.
      :rtype: int


   .. method:: stop(self)
      :async:

      Stop buying keys.


   .. method:: balance(self)
      :async:

      Return current balance of payment channel:

      * ``amount``: The initial amount with which the payment channel was opened.
      * ``remaining``: The remaining amount of XBR in the payment channel that can be spent.
      * ``inflight``: The amount of XBR allocated to buy transactions that are currently processed.

      :return: Current payment balance.
      :rtype: dict


   .. method:: open_channel(self, buyer_addr, amount, details=None)
      :async:

      :param amount:
      :type amount:

      :param details:
      :type details:

      :return:
      :rtype:


   .. method:: close_channel(self, details=None)
      :async:

      Requests to close the currently active payment channel.

      :return:


   .. method:: unwrap(self, key_id, serializer, ciphertext)
      :async:

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


   .. method:: _save_transaction_phase1(self, channel_oid, delegate_adr, buyer_pubkey, key_id, channel_seq, amount, balance, signature)

      :param channel_oid:
      :param delegate_adr:
      :param buyer_pubkey:
      :param key_id:
      :param channel_seq:
      :param amount:
      :param balance:
      :param signature:
      :return:


   .. method:: _save_transaction_phase2(self, channel_oid, delegate_adr, buyer_pubkey, key_id, channel_seq, amount, balance, signature)

      :param channel_oid:
      :param delegate_adr:
      :param buyer_pubkey:
      :param key_id:
      :param channel_seq:
      :param amount:
      :param balance:
      :param signature:
      :return:


   .. method:: past_transactions(self, filter_complete=True, limit=1)

      :param filter_complete:
      :param limit:
      :return:


   .. method:: count_transactions(self)

      :return:


   .. method:: get_transaction(self, key_id)

      :param key_id:
      :return:


   .. method:: is_complete(self, key_id)

      :param key_id:
      :return:



