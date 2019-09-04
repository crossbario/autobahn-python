import sys
import argparse

import web3

from autobahn import xbr

from test_accounts import addr_owner, addr_alice_market, addr_alice_market_maker1, addr_bob_market, addr_bob_market_maker1, \
    addr_charlie_provider, addr_charlie_provider_delegate1, addr_donald_provider, addr_donald_provider_delegate1, \
    addr_edith_consumer, addr_edith_consumer_delegate1, addr_frank_consumer, addr_frank_consumer_delegate1

from test_accounts import hl


def main(accounts):
    for acct in [addr_alice_market, addr_bob_market, addr_charlie_provider, addr_donald_provider, addr_edith_consumer, addr_frank_consumer]:
        level = xbr.xbrnetwork.functions.getMemberLevel(acct).call()
        if not level:
            eula = 'QmU7Gizbre17x6V2VR1Q2GJEjz6m8S1bXmBtVxS2vmvb81'
            profile = ''

            xbr.xbrnetwork.functions.register(eula, profile).transact({'from': acct, 'gas': 200000})
            print('New member {} registered in the XBR Network (eula={}, profile={})'.format(hl(acct), eula, profile))
        else:
            eula = xbr.xbrnetwork.functions.getMemberEula(acct).call()
            profile = xbr.xbrnetwork.functions.getMemberProfile(acct).call()
            print('{} is already a member (level={}, eula={}, profile={})'.format(hl(acct), hl(level), eula, profile))

    DomainStatus_NULL = 0
    DomainStatus_ACTIVE = 1
    DomainStatus_CLOSED = 2

    NodeType_NULL = 0
    NodeType_MASTER = 1
    NodeType_CORE = 2
    NodeType_EDGE = 3

    NodeLicense_NULL = 0
    NodeLicense_INFINITE = 1
    NodeLicense_FREE = 2

    _domain_id = "0x9d9827822252fbe721d45224c7db7cac"
    _domain_key = "0xfeb083ce587a4ea72681d7db776452b05aaf58dc778534a6938313e4c85912f0"
    _license = ""
    _terms = ""
    _meta = ""

    status = xbr.xbrnetwork.functions.getDomainStatus(_domain_id).call()

    if status == DomainStatus_NULL:
        print('Domain does not exist - creating ..')
        xbr.xbrnetwork.functions.createDomain(_domain_id, _domain_key, _license, _terms, _meta).transact({'from': acct, 'gas': 200000})
        print('Domain created')
    elif status == DomainStatus_ACTIVE:
        print('Domain already exists')
    elif status == DomainStatus_CLOSED:
        print('FATAL: domain is closed')
        sys.exit(1)

    _pubkey = '0xf4050a787994fcca715103a83532785d79eaff3e42d18fd3f667fa2bb4af439e'
    _node_id = '0x4570160dd5be4726b2a785499609d6ab'
    _nodeType = NodeType_MASTER
    _nodeLicense = NodeLicense_FREE
    _config = ''

    node = xbr.xbrnetwork.functions.getNodeByKey(_pubkey).call()
    if node == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
        print('Node not yet paired - pairing ..')
        xbr.xbrnetwork.functions.pairNode(_node_id, _domain_id, _nodeType, _nodeLicense, _pubkey, _config).transact({'from': acct, 'gas': 200000})
        print('Node paired!')
    else:
        print('Node already paired')


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
