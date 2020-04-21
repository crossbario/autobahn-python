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

import sys
import uuid
import binascii
import argparse
import random
from pprint import pformat

import eth_keys
import web3
import hashlib
import multihash
import cbor2

import txaio

txaio.use_twisted()

from twisted.internet import reactor
from twisted.internet.error import ReactorNotRunning

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.serializer import CBORSerializer
from autobahn.wamp import cryptosign
from autobahn.wamp.exception import ApplicationError
from autobahn.xbr import pack_uint256

from xbrnetwork import sign_eip712_member_register, sign_eip712_market_create


_COMMANDS = ['onboard', 'onboard-verify', 'create-market', 'create-market-verify']


class Client(ApplicationSession):

    def __init__(self, config=None):
        self.log.info('{klass}.__init__(config={config})', klass=self.__class__.__name__, config=config)

        ApplicationSession.__init__(self, config)

        self._ethkey_raw = config.extra['ethkey']
        self._ethkey = eth_keys.keys.PrivateKey(self._ethkey_raw)
        self._ethadr = web3.Web3.toChecksumAddress(self._ethkey.public_key.to_canonical_address())

        self.log.info("Client (delegate) Ethereum key loaded (adr=0x{adr})",
                      adr=self._ethadr)

        self._key = cryptosign.SigningKey.from_key_bytes(config.extra['cskey'])
        self.log.info("Client (delegate) WAMP-cryptosign authentication key loaded (pubkey=0x{pubkey})",
                      pubkey=self._key.public_key())

        self._running = True

    def onUserError(self, fail, msg):
        self.log.error(msg)
        self.leave('wamp.error', msg)

    def onConnect(self):
        self.log.info('{klass}.onConnect()', klass=self.__class__.__name__)

        authextra = {
            'pubkey': self._key.public_key(),
            'trustroot': None,
            'challenge': None,
            'channel_binding': 'tls-unique'
        }
        self.join(self.config.realm, authmethods=['cryptosign'], authextra=authextra)

    def onChallenge(self, challenge):
        self.log.info('{klass}.onChallenge(challenge={challenge})', klass=self.__class__.__name__, challenge=challenge)

        if challenge.method == 'cryptosign':
            signed_challenge = self._key.sign_challenge(self, challenge)
            return signed_challenge
        else:
            raise RuntimeError('unable to process authentication method {}'.format(challenge.method))

    async def onJoin(self, details):
        self.log.info('{klass}.onJoin(details={details})', klass=self.__class__.__name__, details=details)

        try:
            command = self.config.extra['command']
            if details.authrole == 'anonymous':
                self.log.info('not yet a member in the XBR network')

                assert command in ['onboard', 'onboard-verify']
                if command == 'onboard':
                    username = self.config.extra['username']
                    email = self.config.extra['email']
                    await self._do_onboard_member(username, email)
                elif command == 'onboard-verify':
                    vaction_oid = self.config.extra['vaction']
                    vaction_code = self.config.extra['vcode']
                    await self._do_onboard_member_verify(vaction_oid, vaction_code)
                else:
                    assert False, 'should not arrive here'
            else:
                # WAMP authid on xbrnetwork follows this format: "member-"
                member_oid = uuid.UUID(details.authid[7:])
                member_data = await self.call('network.xbr.console.get_member', member_oid.bytes)
                self.log.info('already a member in the XBR network:\n\n{member_data}\n', member_data=pformat(member_data))

                assert command in ['create-market', 'create-market-verify']
                if command == 'create-market':
                    market_oid = self.config.extra['market']
                    marketmaker = self.config.extra['marketmaker']
                    await self._do_create_market(member_oid, market_oid, marketmaker)
                elif command == 'create-market-verify':
                    vaction_oid = self.config.extra['vaction']
                    vaction_code = self.config.extra['vcode']
                    await self._do_create_market_verify(member_oid, vaction_oid, vaction_code)
                else:
                    assert False, 'should not arrive here'
        except Exception as e:
            self.log.failure()
            self.config.extra['error'] = e
        finally:
            self.leave()

    def onLeave(self, details):
        self.log.info('{klass}.onLeave(details={details})', klass=self.__class__.__name__, details=details)

        self._running = False

        if details.reason == 'wamp.close.normal':
            self.log.info('Shutting down ..')
            # user initiated leave => end the program
            self.config.runner.stop()
            self.disconnect()
        else:
            # continue running the program (let ApplicationRunner perform auto-reconnect attempts ..)
            self.log.info('Will continue to run (reconnect)!')

    def onDisconnect(self):
        self.log.info('{klass}.onDisconnect()', klass=self.__class__.__name__)

        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    async def _do_onboard_member(self, member_username, member_email):
        client_pubkey = binascii.a2b_hex(self._key.public_key())

        # fake wallet type "metamask"
        wallet_type = 'metamask'

        # delegate ethereum private key object
        wallet_key = self._ethkey
        wallet_raw = self._ethkey_raw

        # delegate ethereum account canonical address
        wallet_adr = wallet_key.public_key.to_canonical_address()

        config = await self.call('network.xbr.console.get_config')
        status = await self.call('network.xbr.console.get_status')

        verifyingChain = config['verifying_chain_id']
        verifyingContract = binascii.a2b_hex(config['verifying_contract_adr'][2:])

        registered = status['block']['number']
        eula = config['eula']['hash']

        # create an aux-data object with info only stored off-chain (in our xbrbackend DB) ..
        profile_obj = {
            'member_username': member_username,
            'member_email': member_email,
            'client_pubkey': client_pubkey,
            'wallet_type': wallet_type,
        }

        # .. hash the serialized aux-data object ..
        profile_data = cbor2.dumps(profile_obj)
        h = hashlib.sha256()
        h.update(profile_data)

        # .. compute the sha256 multihash b58-encoded string from that ..
        profile = multihash.to_b58_string(multihash.encode(h.digest(), 'sha2-256'))

        signature = sign_eip712_member_register(wallet_raw, verifyingChain, verifyingContract,
                                                wallet_adr, registered, eula, profile)

        # https://xbr.network/docs/network/api.html#xbrnetwork.XbrNetworkApi.onboard_member
        try:
            result = await self.call('network.xbr.console.onboard_member',
                                     member_username, member_email, client_pubkey, wallet_type, wallet_adr,
                                     verifyingChain, registered, verifyingContract, eula, profile, profile_data,
                                     signature)
        except ApplicationError as e:
            self.log.error('ApplicationError: {error}', error=e)
            self.leave('wamp.error', str(e))
            return
        except Exception as e:
            raise e

        assert type(result) == dict
        assert 'timestamp' in result and type(result['timestamp']) == int and result['timestamp'] > 0
        assert 'action' in result and result['action'] == 'onboard_member'
        assert 'vaction_oid' in result and type(result['vaction_oid']) == bytes and len(result['vaction_oid']) == 16

        vaction_oid = uuid.UUID(bytes=result['vaction_oid'])
        self.log.info('On-boarding member - verification "{vaction_oid}" created', vaction_oid=vaction_oid)

    async def _do_onboard_member_verify(self, vaction_oid, vaction_code):

        self.log.info('Verifying member using vaction_oid={vaction_oid}, vaction_code={vaction_code} ..',
                      vaction_oid=vaction_oid, vaction_code=vaction_code)
        try:
            result = await self.call('network.xbr.console.verify_onboard_member', vaction_oid.bytes, vaction_code)
        except ApplicationError as e:
            self.log.error('ApplicationError: {error}', error=e)
            raise e

        assert type(result) == dict
        assert 'member_oid' in result and type(result['member_oid']) == bytes and len(result['member_oid']) == 16
        assert 'created' in result and type(result['created']) == int and result['created'] > 0

        member_oid = result['member_oid']
        self.log.info('SUCCESS! New XBR Member onboarded: member_oid={member_oid}, result=\n{result}',
                      member_oid=uuid.UUID(bytes=member_oid), result=pformat(result))

    async def _do_create_market(self, member_oid, market_oid, marketmaker, provider_security=0, consumer_security=0, market_fee=0):
        member_data = await self.call('network.xbr.console.get_member', member_oid.bytes)
        member_adr = member_data['address']

        config = await self.call('network.xbr.console.get_config')

        verifyingChain = config['verifying_chain_id']
        verifyingContract = binascii.a2b_hex(config['verifying_contract_adr'][2:])

        coin_adr = binascii.a2b_hex(config['contracts']['xbrtoken'][2:])

        status = await self.call('network.xbr.console.get_status')
        block_number = status['block']['number']

        # count all markets before we create a new one:
        res = await self.call('network.xbr.console.find_markets')
        cnt_market_before = len(res)
        self.log.info('Total markets before: {cnt_market_before}', cnt_market_before=cnt_market_before)

        res = await self.call('network.xbr.console.get_markets_by_owner', member_oid.bytes)
        cnt_market_by_owner_before = len(res)
        self.log.info('Market for owner: {cnt_market_by_owner_before}',
                      cnt_market_by_owner_before=cnt_market_by_owner_before)

        # collect information for market creation that is stored on-chain

        # terms text: encode in utf8 and compute BIP58 multihash string
        terms_data = 'these are my market terms (randint={})'.format(random.randint(0, 1000)).encode('utf8')
        h = hashlib.sha256()
        h.update(terms_data)
        terms_hash = str(multihash.to_b58_string(multihash.encode(h.digest(), 'sha2-256')))

        # market meta data that doesn't change. the hash of this is part of the data that is signed and also
        # stored on-chain (only the hash, not the meta data!)
        meta_obj = {
            'chain_id': verifyingChain,
            'block_number': block_number,
            'contract_adr': verifyingContract,
            'member_adr': member_adr,
            'member_oid': member_oid.bytes,
            'market_oid': market_oid.bytes,
        }
        meta_data = cbor2.dumps(meta_obj)
        h = hashlib.sha256()
        h.update(meta_data)
        meta_hash = multihash.to_b58_string(multihash.encode(h.digest(), 'sha2-256'))

        # create signature for pre-signed transaction
        signature = sign_eip712_market_create(self._ethkey_raw, verifyingChain, verifyingContract, member_adr,
                                              block_number, market_oid.bytes, coin_adr, terms_hash, meta_hash,
                                              marketmaker, provider_security, consumer_security, market_fee)

        # for wire transfer, convert to bytes
        provider_security = pack_uint256(provider_security)
        consumer_security = pack_uint256(consumer_security)
        market_fee = pack_uint256(market_fee)

        # market settings that can change. even though changing might require signing, neither the data nor
        # and signatures are stored on-chain. however, even when only signed off-chain, this establishes
        # a chain of signature anchored in the on-chain record for this market!
        attributes = {
            'title': 'International Data Monetization Award',
            'label': 'IDMA',
            'homepage': 'https://markets.international-data-monetization-award.com/',
        }

        # now provide everything of above:
        #   - market operator (owning member) and market oid
        #   - signed market data and signature
        #   - settings
        createmarket_request_submitted = await self.call('network.xbr.console.create_market', member_oid.bytes,
                                                         market_oid.bytes, verifyingChain, block_number,
                                                         verifyingContract, coin_adr, terms_hash, meta_hash, meta_data,
                                                         marketmaker, provider_security, consumer_security, market_fee,
                                                         signature, attributes)

        self.log.info('SUCCESS: Create market request submitted: \n{createmarket_request_submitted}\n',
                      createmarket_request_submitted=pformat(createmarket_request_submitted))

        assert type(createmarket_request_submitted) == dict
        assert 'timestamp' in createmarket_request_submitted and type(
            createmarket_request_submitted['timestamp']) == int and createmarket_request_submitted['timestamp'] > 0
        assert 'action' in createmarket_request_submitted and createmarket_request_submitted[
            'action'] == 'create_market'
        assert 'vaction_oid' in createmarket_request_submitted and type(
            createmarket_request_submitted['vaction_oid']) == bytes and len(
            createmarket_request_submitted['vaction_oid']) == 16

        vaction_oid = uuid.UUID(bytes=createmarket_request_submitted['vaction_oid'])
        self.log.info('SUCCESS: New Market verification "{vaction_oid}" created', vaction_oid=vaction_oid)

    async def _do_create_market_verify(self, member_oid, vaction_oid, vaction_code):
        self.log.info('Verifying create market using vaction_oid={vaction_oid}, vaction_code={vaction_code} ..',
                      vaction_oid=vaction_oid, vaction_code=vaction_code)

        create_market_request_verified = await self.call('network.xbr.console.verify_create_market', vaction_oid.bytes,
                                                         vaction_code)

        self.log.info('Create market request verified: \n{create_market_request_verified}\n',
                      create_market_request_verified=pformat(create_market_request_verified))

        assert type(create_market_request_verified) == dict
        assert 'market_oid' in create_market_request_verified and type(
            create_market_request_verified['market_oid']) == bytes and len(
            create_market_request_verified['market_oid']) == 16
        assert 'created' in create_market_request_verified and type(
            create_market_request_verified['created']) == int and create_market_request_verified['created'] > 0

        market_oid = create_market_request_verified['market_oid']
        self.log.info('SUCCESS! New XBR market created: market_oid={market_oid}, result=\n{result}',
                      market_oid=uuid.UUID(bytes=market_oid), result=pformat(create_market_request_verified))

        market_oids = await self.call('network.xbr.console.find_markets')
        self.log.info('SUCCESS - find_markets: found {cnt_markets} markets', cnt_markets=len(market_oids))

        # count all markets after we created a new market:
        cnt_market_after = len(market_oids)
        self.log.info('Total markets after: {cnt_market_after}', cnt_market_after=cnt_market_after)
        assert market_oid in market_oids, 'expected to find market ID {}, but not found in {} returned market IDs'.format(
            uuid.UUID(bytes=market_oid), len(market_oids))

        market_oids = await self.call('network.xbr.console.get_markets_by_owner', member_oid.bytes)
        self.log.info('SUCCESS - get_markets_by_owner: found {cnt_markets} markets', cnt_markets=len(market_oids))

        # count all markets after we created a new market:
        cnt_market_by_owner_after = len(market_oids)
        self.log.info('Market for owner: {cnt_market_by_owner_after}',
                      cnt_market_by_owner_before=cnt_market_by_owner_after)
        assert market_oid in market_oids, 'expected to find market ID {}, but not found in {} returned market IDs'.format(
            uuid.UUID(bytes=market_oid), len(market_oids))

        for market_oid in market_oids:
            self.log.info('network.xbr.console.get_market(market_oid={market_oid}) ..', market_oid=market_oid)
            market = await self.call('network.xbr.console.get_market', market_oid, include_attributes=True)
            self.log.info('SUCCESS: got market information\n\n{market}\n', market=pformat(market))


def _main():
    parser = argparse.ArgumentParser()

    parser.add_argument('command', type=str, choices=_COMMANDS,
                        help='Command to run')

    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help='Enable debug output.')

    parser.add_argument('--url',
                        dest='url',
                        type=str,
                        default='wss://planet.xbr.network/ws',
                        help='The router URL (default: "wss://planet.xbr.network/ws").')

    parser.add_argument('--realm',
                        dest='realm',
                        type=str,
                        default='xbrnetwork',
                        help='The realm to join (default: "xbrnetwork").')

    parser.add_argument('--ethkey',
                        dest='ethkey',
                        type=str,
                        help='Private Ethereum key (32 bytes as HEX encoded string)')

    parser.add_argument('--cskey',
                        dest='cskey',
                        type=str,
                        help='Private WAMP-cryptosign authentication key (32 bytes as HEX encoded string)')

    parser.add_argument('--username',
                        dest='username',
                        type=str,
                        default=None,
                        help='For on-boarding, the new member username.')

    parser.add_argument('--email',
                        dest='email',
                        type=str,
                        default=None,
                        help='For on-boarding, the new member email address.')

    parser.add_argument('--market',
                        dest='market',
                        type=str,
                        default=None,
                        help='For creating new markets, the market UUID.')

    parser.add_argument('--marketmaker',
                        dest='marketmaker',
                        type=str,
                        default=None,
                        help='For creating new markets, the market maker address.')

    parser.add_argument('--vcode',
                        dest='vcode',
                        type=str,
                        default=None,
                        help='For verifications of actions, the verification UUID.')

    parser.add_argument('--vaction',
                        dest='vaction',
                        type=str,
                        default=None,
                        help='For verifications of actions (on-board, create-market, ..), the verification code.')

    args = parser.parse_args()

    if args.debug:
        txaio.start_logging(level='debug')
    else:
        txaio.start_logging(level='info')

    extra = {
        'command': args.command,
        'ethkey': binascii.a2b_hex(args.ethkey[2:]),
        'cskey': binascii.a2b_hex(args.cskey[2:]),
        'username': args.username,
        'email': args.email,
        'market': uuid.UUID(args.market) if args.market else None,
        'marketmaker': binascii.a2b_hex(args.marketmaker[2:]) if args.marketmaker else None,
        'vcode': args.vcode,
        'vaction': uuid.UUID(args.vaction) if args.vaction else None,
    }
    runner = ApplicationRunner(url=args.url, realm=args.realm, extra=extra, serializers=[CBORSerializer()])

    try:
        runner.run(Client, auto_reconnect=False)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    _main()
