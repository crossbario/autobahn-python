:mod:`autobahn.xbr._eip712_node_pair`
=====================================

.. py:module:: autobahn.xbr._eip712_node_pair


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_node_pair._create_eip712_node_pair
   autobahn.xbr._eip712_node_pair.sign_eip712_node_pair
   autobahn.xbr._eip712_node_pair.recover_eip712_node_pair


.. function:: _create_eip712_node_pair(chainId: int, verifyingContract: bytes, member: bytes, paired: int, nodeId: bytes, domainId: bytes, nodeType: int, nodeKey: bytes, config: Optional[str]) -> dict

   :param chainId:
   :param verifyingContract:
   :param member:
   :param joined:
   :param marketId:
   :param actorType:
   :param meta:
   :return:


.. function:: sign_eip712_node_pair(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, paired: int, nodeId: bytes, domainId: bytes, nodeType: int, nodeKey: bytes, config: Optional[str]) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_node_pair(chainId: int, verifyingContract: bytes, member: bytes, paired: int, nodeId: bytes, domainId: bytes, nodeType: int, nodeKey: bytes, config: str, signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


