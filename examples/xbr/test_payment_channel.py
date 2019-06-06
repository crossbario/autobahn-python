import os
import sys
import binascii

import web3
from autobahn import xbr

from test_accounts import addr_owner, addr_edith_consumer, addr_frank_consumer, markets, hl


def main(w3, accounts):
    for market in markets:
        for actor in market['actors']:
            if actor['type'] == xbr.ActorType.CONSUMER:

                amount = 100 * 10**18

                result = xbr.xbrToken.functions.approve(xbr.xbrNetwork.address, amount).transact({'from': actor['addr'], 'gas': 1000000})
                if not result:
                    print('Failed to allow transfer of tokens for payment channel!', result)
                else:
                    print('Allowed transfer of {} XBR from {} to {} for opening a payment channel'.format(amount, actor['addr'], xbr.xbrNetwork.address))

                    # openPaymentChannel (bytes16 marketId, address consumerDelegate, uint256 amount) public returns (address paymentChannel)
                    txn = xbr.xbrNetwork.functions.openPaymentChannel(market['id'], actor['delegate'], amount).transact({'from': actor['addr'], 'gas': 1000000})
                    receipt = w3.eth.getTransactionReceipt(txn)

                    # bytes16 marketId, address sender, address delegate, address receiver, address channel
                    args = xbr.xbrNetwork.events.PaymentChannelCreated().processReceipt(receipt)
                    args = args[0].args

                    marketId = args['marketId']
                    sender = args['sender']
                    delegate = args['delegate']
                    recipient = args['receiver']
                    channel = args['channel']

                    print('Actor {} opened payment channel {} in market {} with inital deposit of {}, delegate {} and recipient {}!'.format(actor['addr'], hl(channel), market['id'], amount, hl(delegate), recipient))


if __name__ == '__main__':
    print('using web3.py v{}'.format(web3.__version__))

    # using automatic provider detection:
    from web3.auto import w3

    # check we are connected, and check network ID
    if not w3.isConnected():
        print('could not connect to Web3/Ethereum')
        sys.exit(1)
    else:
        print('connected to network {}'.format(w3.version.network))

    # set new provider on XBR library
    xbr.setProvider(w3)

    # now enter main ..
    main(w3, w3.eth.accounts)
