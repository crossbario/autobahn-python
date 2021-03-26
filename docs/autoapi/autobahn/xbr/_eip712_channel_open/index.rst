:mod:`autobahn.xbr._eip712_channel_open`
========================================

.. py:module:: autobahn.xbr._eip712_channel_open


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_channel_open._create_eip712_channel_open
   autobahn.xbr._eip712_channel_open.sign_eip712_channel_open
   autobahn.xbr._eip712_channel_open.recover_eip712_channel_open


.. function:: _create_eip712_channel_open(chainId: int, verifyingContract: bytes, ctype: int, openedAt: int, marketId: bytes, channelId: bytes, actor: bytes, delegate: bytes, marketmaker: bytes, recipient: bytes, amount: int) -> dict

   :param chainId:
   :param verifyingContract:
   :param ctype:
   :param openedAt:
   :param marketId:
   :param channelId:
   :param actor:
   :param delegate:
   :param marketmaker:
   :param recipient:
   :param amount:
   :return:


.. function:: sign_eip712_channel_open(eth_privkey: bytes, chainId: int, verifyingContract: bytes, ctype: int, openedAt: int, marketId: bytes, channelId: bytes, actor: bytes, delegate: bytes, marketmaker: bytes, recipient: bytes, amount: int) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_channel_open(chainId: int, verifyingContract: bytes, ctype: int, openedAt: int, marketId: bytes, channelId: bytes, actor: bytes, delegate: bytes, marketmaker: bytes, recipient: bytes, amount: int, signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


