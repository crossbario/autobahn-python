:mod:`autobahn.xbr._blockchain`
===============================

.. py:module:: autobahn.xbr._blockchain


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.xbr._blockchain.SimpleBlockchain



.. class:: SimpleBlockchain(gateway=None)


   Bases: :class:`object`

   Simple Ethereum blockchain XBR client.

   .. attribute:: DomainStatus_NULL
      :annotation: = 0

      

   .. attribute:: DomainStatus_ACTIVE
      :annotation: = 1

      

   .. attribute:: DomainStatus_CLOSED
      :annotation: = 2

      

   .. attribute:: NodeType_NULL
      :annotation: = 0

      

   .. attribute:: NodeType_MASTER
      :annotation: = 1

      

   .. attribute:: NodeType_CORE
      :annotation: = 2

      

   .. attribute:: NodeType_EDGE
      :annotation: = 3

      

   .. attribute:: NodeLicense_NULL
      :annotation: = 0

      

   .. attribute:: NodeLicense_INFINITE
      :annotation: = 1

      

   .. attribute:: NodeLicense_FREE
      :annotation: = 2

      

   .. attribute:: log
      

      

   .. attribute:: backgroundCaller
      

      

   .. method:: start(self)

      Start the blockchain client using the configured blockchain gateway.


   .. method:: stop(self)

      Stop the blockchain client.


   .. method:: get_market_status(self, market_id)
      :async:

      :param market_id:
      :return:


   .. method:: get_domain_status(self, domain_id)
      :async:

      :param domain_id:
      :type domain_id: bytes

      :return:
      :rtype: dict


   .. method:: get_node_status(self, delegate_adr)
      :abstractmethod:

      :param delegate_adr:
      :type delegate_adr: bytes

      :return:
      :rtype: dict


   .. method:: get_actor_status(self, delegate_adr)
      :abstractmethod:

      :param delegate_adr:
      :type delegate_adr: bytes

      :return:
      :rtype: dict


   .. method:: get_delegate_status(self, delegate_adr)
      :abstractmethod:

      :param delegate_adr:
      :type delegate_adr: bytes

      :return:
      :rtype: dict


   .. method:: get_channel_status(self, channel_adr)
      :abstractmethod:

      :param channel_adr:
      :type channel_adr: bytes

      :return:
      :rtype: dict


   .. method:: get_member_status(self, member_adr)
      :async:

      :param member_adr:
      :type member_adr: bytes

      :return:
      :rtype: dict


   .. method:: get_balances(self, account_adr)
      :async:

      Return current ETH and XBR balances of account with given address.

      :param account_adr: Ethereum address of account to get balances for.
      :type account_adr: bytes

      :return: A dictionary with ``"ETH"`` and ``"XBR"`` keys and respective
          current on-chain balances as values.
      :rtype: dict


   .. method:: get_contract_adrs(self)

      Get XBR smart contract addresses.

      :return: A dictionary with ``"XBRToken"``  and ``"XBRNetwork"`` keys and Ethereum
          contract addresses as values.
      :rtype: dict



