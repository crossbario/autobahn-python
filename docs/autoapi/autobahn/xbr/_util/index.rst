:mod:`autobahn.xbr._util`
=========================

.. py:module:: autobahn.xbr._util


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._util.make_w3
   autobahn.xbr._util.unpack_uint128
   autobahn.xbr._util.pack_uint128
   autobahn.xbr._util.unpack_uint256
   autobahn.xbr._util.pack_uint256
   autobahn.xbr._util.hl
   autobahn.xbr._util._qn
   autobahn.xbr._util.hltype
   autobahn.xbr._util.hlid
   autobahn.xbr._util.hluserid
   autobahn.xbr._util.hlval
   autobahn.xbr._util.hlcontract
   autobahn.xbr._util.with_0x
   autobahn.xbr._util.without_0x


.. function:: make_w3(gateway_config=None)

   Create a Web3 instance configured and ready-to-use gateway to the blockchain.

   :param gateway_config: Blockchain gateway configuration.
   :type gateway_config: dict

   :return: Configured Web3 instance.
   :rtype: :class:`web3.Web3`


.. function:: unpack_uint128(data)


.. function:: pack_uint128(value)


.. function:: unpack_uint256(data)


.. function:: pack_uint256(value)


.. function:: hl(text, bold=False, color='yellow')


.. function:: _qn(obj)


.. function:: hltype(obj)


.. function:: hlid(oid)


.. function:: hluserid(oid)


.. function:: hlval(val, color='green')


.. function:: hlcontract(oid)


.. function:: with_0x(address)


.. function:: without_0x(address)


