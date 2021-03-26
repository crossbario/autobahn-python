:mod:`autobahn.xbr._eip712_channel_close`
=========================================

.. py:module:: autobahn.xbr._eip712_channel_close


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_channel_close._create_eip712_channel_close
   autobahn.xbr._eip712_channel_close.sign_eip712_channel_close
   autobahn.xbr._eip712_channel_close.recover_eip712_channel_close


.. function:: _create_eip712_channel_close(chainId: int, verifyingContract: bytes, closeAt: int, marketId: bytes, channelId: bytes, channelSeq: int, balance: int, isFinal: bool) -> dict

   :param chainId:
   :param verifyingContract:
   :param marketId:
   :param channelId:
   :param channelSeq:
   :param balance:
   :param isFinal:
   :return:


.. function:: sign_eip712_channel_close(eth_privkey: bytes, chainId: int, verifyingContract: bytes, closeAt: int, marketId: bytes, channelId: bytes, channelSeq: int, balance: int, isFinal: bool) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_channel_close(chainId: int, verifyingContract: bytes, closeAt: int, marketId: bytes, channelId: bytes, channelSeq: int, balance: int, isFinal: bool, signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


