# XBR test accounts, generated from seed phrase:
# myth like bonus scare over problem client lizard pioneer submit female collect

# export XBR_DEBUG_TOKEN_ADDR="0xcfeb869f69431e42cdb54a4f4f105c19c080a601"
# export XBR_DEBUG_NETWORK_ADDR="0x254dffcd3277c0b1660f6d42efbb754edababc2b"

import web3
from autobahn import xbr
import click
import six


def hl(text, bold=True, color='yellow'):
    if not isinstance(text, six.text_type):
        text = '{}'.format(text)
    return click.style(text, fg=color, bold=bold)


# the XBR Project
addr_owner = web3.Web3.toChecksumAddress('0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1')

# 2 test XBR market owners
addr_alice_market = web3.Web3.toChecksumAddress('0xffcf8fdee72ac11b5c542428b35eef5769c409f0')
addr_alice_market_maker1 = web3.Web3.toChecksumAddress('0x22d491bde2303f2f43325b2108d26f1eaba1e32b')

addr_bob_market = web3.Web3.toChecksumAddress('0xe11ba2b4d45eaed5996cd0823791e0c93114882d')
addr_bob_market_maker1 = web3.Web3.toChecksumAddress('0xd03ea8624c8c5987235048901fb614fdca89b117')

# 2 test XBR data providers
addr_charlie_provider = web3.Web3.toChecksumAddress('0x95ced938f7991cd0dfcb48f0a06a40fa1af46ebc')
addr_charlie_provider_delegate1 = web3.Web3.toChecksumAddress('0x3e5e9111ae8eb78fe1cc3bb8915d5d461f3ef9a9')

addr_donald_provider = web3.Web3.toChecksumAddress('0x28a8746e75304c0780e011bed21c72cd78cd535e')
addr_donald_provider_delegate1 = web3.Web3.toChecksumAddress('0xaca94ef8bd5ffee41947b4585a84bda5a3d3da6e')

# 2 test XBR data consumers
addr_edith_consumer = web3.Web3.toChecksumAddress('0x1df62f291b2e969fb0849d99d9ce41e2f137006e')
addr_edith_consumer_delegate1 = web3.Web3.toChecksumAddress('0x610bb1573d1046fcb8a70bbbd395754cd57c2b60')

addr_frank_consumer = web3.Web3.toChecksumAddress('0x855fa758c77d68a04990e992aa4dcdef899f654a')
addr_frank_consumer_delegate1 = web3.Web3.toChecksumAddress('0xfa2435eacf10ca62ae6787ba2fb044f8733ee843')


accounts = [
	addr_owner,
	addr_alice_market,
	addr_alice_market_maker1,
	addr_bob_market,
	addr_bob_market_maker1,
	addr_charlie_provider,
	addr_charlie_provider_delegate1,
	addr_donald_provider,
	addr_donald_provider_delegate1,
	addr_edith_consumer,
	addr_edith_consumer_delegate1,
	addr_frank_consumer,
	addr_frank_consumer_delegate1
]


markets = [
    {
        # '0x' + os.urandom(16).hex()
        'id': '0xa1b8d6741ae8492017fafd8d4f8b67a2',
        'owner': addr_alice_market,
        'maker': addr_alice_market_maker1,
        'terms': '',
        'meta': '',
        'providerSecurity': 100 * 1000,
        'consumerSecurity': 100 * 1000,
        'marketFee': 1000,
        'actors': [
            {
                'addr': addr_charlie_provider,
                'type': xbr.ActorType.PROVIDER,
                'security': 100 * 1000
            },
            {
                'addr': addr_donald_provider,
                'type': xbr.ActorType.PROVIDER,
                'security': 100 * 1000
            },
            {
                'addr': addr_edith_consumer,
                'type': xbr.ActorType.CONSUMER,
                'security': 100 * 1000,
                'delegate': addr_edith_consumer_delegate1
            },
            {
                'addr': addr_frank_consumer,
                'type': xbr.ActorType.CONSUMER,
                'security': 100 * 1000,
                'delegate': addr_frank_consumer_delegate1
            }
        ]
    },
    {
        'id': '0xa42474d7e8ed084e13d22690f9d002d5',
        'owner': addr_bob_market,
        'maker': addr_bob_market_maker1,
        'terms': '',
        'meta': '',
        'providerSecurity': 100 * 1000,
        'consumerSecurity': 100 * 1000,
        'marketFee': 1000,
        'actors': []
    }
]
