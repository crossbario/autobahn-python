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
import os
import uuid
import binascii
import argparse
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

from xbrnetwork import sign_eip712_member_register

_CFX_VERIFICATIONS_DIR = '../../../xbr-www/cloud/planet_xbr_crossbarfx/.crossbar/.verifications'

_COMMANDS = ['onboard', 'onboard-verify']


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

                assert command in [], 'should not arrive here'
        except Exception as e:
            self.log.failure()
            self.config.extra['error'] = e
        finally:
            self.leave()

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
