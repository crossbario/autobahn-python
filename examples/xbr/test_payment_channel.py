import os
import sys
import binascii
import argparse

import web3

from autobahn import xbr

from test_accounts import addr_owner, addr_edith_consumer, addr_frank_consumer, markets, hl


def main(accounts):
    for market in markets:
        for actor in market['actors']:
            if actor['type'] == xbr.ActorType.CONSUMER:

                amount = 100 * 10**18

                result = xbr.xbrtoken.functions.approve(xbr.xbrnetwork.address, amount).transact({'from': actor['addr'], 'gas': 1000000})
                if not result:
                    print('Failed to allow transfer of tokens for payment channel!', result)
                else:
                    print('Allowed transfer of {} XBR from {} to {} for opening a payment channel'.format(amount, actor['addr'], xbr.xbrnetwork.address))

                    # openPaymentChannel (bytes16 marketId, address consumerDelegate, uint256 amount) public returns (address paymentChannel)
                    txn = xbr.xbrnetwork.functions.openPaymentChannel(market['id'], actor['delegate'], amount).transact({'from': actor['addr'], 'gas': 1000000})
                    receipt = w3.eth.getTransactionReceipt(txn)

                    # bytes16 marketId, address sender, address delegate, address receiver, address channel
                    args = xbr.xbrnetwork.events.PaymentChannelCreated().processReceipt(receipt)
                    args = args[0].args

                    marketId = args['marketId']
                    sender = args['sender']
                    delegate = args['delegate']
                    recipient = args['receiver']
                    channel = args['channel']

                    print('Actor {} opened payment channel {} in market {} with initial deposit of {}, delegate {} and recipient {}!'.format(actor['addr'], hl(channel), market['id'], amount, hl(delegate), recipient))


if __name__ == '__main__':
    print('using web3.py v{}'.format(web3.__version__))

    parser = argparse.ArgumentParser()

    parser.add_argument('--gateway',
                        dest='gateway',
                        type=str,
                        default=None,
                        help='Ethereum HTTP gateway URL or None for auto-select (default: -, means let web3 auto-select).')

    args = parser.parse_args()

    if args.gateway:
        w3 = web3.Web3(web3.Web3.HTTPProvider(args.gateway))
    else:
        # using automatic provider detection:
        from web3.auto import w3

    # check we are connected, and check network ID
    if not w3.isConnected():
        print('could not connect to Web3/Ethereum at: {}'.format(args.gateway or 'auto'))
        sys.exit(1)
    else:
        print('connected via provider "{}"'.format(args.gateway or 'auto'))

    # set new provider on XBR library
    xbr.setProvider(w3)

    # now enter main ..
    main(w3.eth.accounts)
