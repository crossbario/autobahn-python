import os
import sys
import web3

from autobahn import xbr

from test_accounts import addr_owner, addr_alice_market, addr_alice_market_maker1, addr_bob_market, addr_bob_market_maker1, \
    addr_charlie_provider, addr_charlie_provider_delegate1, addr_donald_provider, addr_donald_provider_delegate1, \
    addr_edith_consumer, addr_edith_consumer_delegate1, addr_frank_consumer, addr_frank_consumer_delegate1

from test_accounts import markets, hl

def main(accounts):
    for market in markets:
        owner = xbr.xbrNetwork.functions.getMarketOwner(market['id']).call()

        if owner != '0x0000000000000000000000000000000000000000':
            if owner != market['owner']:
                print('Market {} already exists, but has wrong owner!! Expected {}, but owner is {}'.format(market['id'], market['owner'], owner))
            else:
                print('Market {} already exists and has expected owner {}'.format(hl(market['id']), owner))
        else:
            xbr.xbrNetwork.functions.createMarket(
                market['id'],
                market['terms'],
                market['meta'],
                market['maker'],
                market['providerSecurity'],
                market['consumerSecurity'],
                market['marketFee']).transact({'from': market['owner'], 'gas': 1000000})

            print('Market {} created with owner!'.format(hl(market['id']), market['owner']))

        for actor in market['actors']:
            atype = xbr.xbrNetwork.functions.getMarketActorType(market['id'], actor['addr']).call()
            if atype:
                if atype != actor['type']:
                    print('Account {} is already actor in the market, but has wrong actor type! Expected {}, but got {}.'.format(actor['addr'], actor['type'], atype))
                else:
                    print('Account {} is already actor in the market and has correct actor type {}'.format(actor['addr'], atype))
            else:
                result = xbr.xbrToken.functions.approve(xbr.xbrNetwork.address, actor['security']).transact({'from': actor['addr'], 'gas': 1000000})
                if not result:
                    print('Failed to allow transfer of tokens for market security!', result)
                else:
                    print('Allowed transfer of {} XBR from {} to {} as security for joining market'.format(actor['security'], actor['addr'], xbr.xbrNetwork.address))

                    security = xbr.xbrNetwork.functions.joinMarket(market['id'], actor['type']).transact({'from': actor['addr'], 'gas': 1000000})

                    print('Actor {} joined market {} as actor type {} with security {}!'.format(hl(actor['addr']), market['id'], hl(actor['type']), security))


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
    main(w3.eth.accounts)
