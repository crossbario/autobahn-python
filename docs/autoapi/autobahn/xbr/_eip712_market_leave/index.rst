:mod:`autobahn.xbr._eip712_market_leave`
========================================

.. py:module:: autobahn.xbr._eip712_market_leave


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_market_leave._create_eip712_market_leave
   autobahn.xbr._eip712_market_leave.sign_eip712_market_leave
   autobahn.xbr._eip712_market_leave.recover_eip712_market_leave


.. function:: _create_eip712_market_leave(chainId: int, verifyingContract: bytes, member: bytes, left: int, marketId: bytes, actorType: int) -> dict

   :param chainId:
   :param verifyingContract:
   :param member:
   :param joined:
   :param marketId:
   :param actorType:
   :param meta:
   :return:


.. function:: sign_eip712_market_leave(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, left: int, marketId: bytes, actorType: int) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_market_leave(chainId: int, verifyingContract: bytes, member: bytes, left: int, marketId: bytes, actorType: int, signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


