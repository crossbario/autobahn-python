###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import txaio
txaio.use_twisted()

from twisted.internet.threads import deferToThread

import web3
from autobahn import xbr


class SimpleBlockchain(object):
    """
    Simple Ethereum blockchain XBR client.
    """

    log = txaio.make_logger()

    def __init__(self, gateway=None):
        """

        :param gateway: Optional explicit Ethereum gateway URL to use.
            If no explicit gateway is specified, let web3 auto-choose.
        :type gateway: str
        """
        self._gateway = gateway
        self._w3 = None

    def start(self):
        """
        Start the blockchain client using the configured blockchain gateway.
        """
        assert self._w3 is None

        if self._gateway:
            w3 = web3.Web3(web3.Web3.HTTPProvider(self._gateway))
        else:
            # using automatic provider detection:
            from web3.auto import w3

        # check we are connected, and check network ID
        if not w3.isConnected():
            emsg = 'could not connect to Web3/Ethereum at: {}'.format(self._gateway or 'auto')
            self.log.warn(emsg)
            raise RuntimeError(emsg)
        else:
            print('connected to network {} at provider "{}"'.format(w3.version.network,
                                                                    self._gateway or 'auto'))

        self._w3 = w3

        # set new provider on XBR library
        xbr.setProvider(self._w3)

    def stop(self):
        """
        Stop the blockchain client.
        """
        assert self._w3 is not None

        self._w3 = None

    def get_balances(self, adr):
        """
        Return current ETH and XBR balances of account with given address.

        :param adr: Ethereum address of account to get balances for.
        :return: A dictionary with ``"ETH"`` and ``"XBR"`` keys and respective
            current on-chain balances as values.
        :rtype: dict
        """
        def _balance(_adr):
            balance_eth = self._w3.eth.getBalance(_adr)
            balance_xbr = xbr.xbrtoken.functions.balanceOf(_adr).call()
            return {
                'ETH': balance_eth,
                'XBR': balance_xbr,
            }

        d = deferToThread(_balance, adr)
        return d

    def get_contract_adrs(self):
        """
        Get XBR smart contract addresses.

        :return: A dictionary with ``"XBRToken"``  and ``"XBRNetwork"`` keys and Ethereum
            contract addresses as values.
        :rtype: dict
        """
        return {
            'XBRToken': xbr.xbrtoken.address,
            'XBRNetwork': xbr.xbrnetwork.address,
        }
