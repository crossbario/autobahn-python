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

import os
import io
import sys
import uuid
import struct
import binascii
import configparser
from typing import Optional, List, Dict

import click
import nacl
import web3
import numpy as np
from time import time_ns
from eth_utils.conversions import hexstr_if_str, to_hex

from autobahn.websocket.util import parse_url
from autobahn.xbr._util import hlval, hltype
from autobahn.xbr._wallet import pkm_from_argon2_secret

_HAS_COLOR_TERM = False
try:
    import colorama

    # https://github.com/tartley/colorama/issues/48
    term = None
    if sys.platform == 'win32' and 'TERM' in os.environ:
        term = os.environ.pop('TERM')

    colorama.init()
    _HAS_COLOR_TERM = True

    if term:
        os.environ['TERM'] = term

except ImportError:
    pass


class Profile(object):
    """
    User profile, stored as named section in ``${HOME}/.xbrnetwork/config.ini``.
    """

    def __init__(self,
                 path: Optional[str] = None,
                 name: Optional[str] = None,
                 ethkey: Optional[bytes] = None,
                 cskey: Optional[bytes] = None,
                 username: Optional[str] = None,
                 email: Optional[str] = None,
                 network_url: Optional[str] = None,
                 network_realm: Optional[str] = None,
                 vaction_oid: Optional[uuid.UUID] = None,
                 vaction_requested: Optional[np.datetime64] = None,
                 vaction_verified: Optional[np.datetime64] = None,
                 market_url: Optional[str] = None,
                 market_realm: Optional[str] = None,
                 infura_url: Optional[str] = None,
                 infura_network: Optional[str] = None,
                 infura_key: Optional[str] = None,
                 infura_secret: Optional[str] = None):
        """

        :param path:
        :param name:
        :param ethkey:
        :param cskey:
        :param username:
        :param email:
        :param network_url:
        :param network_realm:
        :param vaction_oid:
        :param vaction_requested:
        :param vaction_verified:
        :param market_url:
        :param market_realm:
        :param infura_url:
        :param infura_network:
        :param infura_key:
        :param infura_secret:
        """
        from txaio import make_logger
        self.log = make_logger()

        self.path = path
        self.name = name
        self.ethkey = ethkey
        self.cskey = cskey
        self.username = username
        self.email = email
        self.network_url = network_url
        self.network_realm = network_realm
        self.vaction_oid = vaction_oid
        self.vaction_requested = vaction_requested
        self.vaction_verified = vaction_verified
        self.market_url = market_url
        self.market_realm = market_realm
        self.infura_url = infura_url
        self.infura_network = infura_network
        self.infura_key = infura_key
        self.infura_secret = infura_secret

    def marshal(self):
        ethkey = '0x{}'.format(binascii.b2a_hex(self.ethkey).decode()) if self.ethkey else ''
        cskey = '0x{}'.format(binascii.b2a_hex(self.cskey).decode()) if self.cskey else ''
        obj = {}
        obj['path'] = self.path or ''
        obj['name'] = self.name or ''
        obj['ethkey'] = ethkey or ''
        obj['cskey'] = cskey or ''
        obj['username'] = self.username or ''
        obj['email'] = self.email or ''
        obj['network_url'] = self.network_url or ''
        obj['network_realm'] = self.network_realm or ''
        obj['vaction_oid'] = str(self.vaction_oid) if self.vaction_oid else ''
        obj['vaction_requested'] = str(self.vaction_requested) if self.vaction_requested else ''
        obj['vaction_verified'] = str(self.vaction_verified) if self.vaction_verified else ''
        obj['market_url'] = self.market_url or ''
        obj['market_realm'] = self.market_realm or ''
        obj['infura_url'] = self.infura_url or ''
        obj['infura_network'] = self.infura_network or ''
        obj['infura_key'] = self.infura_key or ''
        obj['infura_secret'] = self.infura_secret or ''
        return obj

    @staticmethod
    def parse(path, name, items):
        ethkey = None
        cskey = None
        username = None
        email = None
        network_url = None
        network_realm = None
        vaction_oid = None
        vaction_requested = None
        vaction_verified = None
        market_url = None
        market_realm = None
        infura_network = None
        infura_key = None
        infura_secret = None
        infura_url = None
        for k, v in items:
            if k == 'network_url':
                network_url = str(v)
            elif k == 'network_realm':
                network_realm = str(v)
            elif k == 'vaction_oid':
                if type(v) == bytes:
                    vaction_oid = uuid.UUID(bytes=v)
                elif type(v) == str:
                    vaction_oid = uuid.UUID(v)
                else:
                    raise ValueError('invalid type {} for vaction_oid'.format(type(v)))
            elif k == 'vaction_requested':
                if type(v) == int:
                    vaction_requested = np.datetime64(v, 'ns')
                else:
                    raise ValueError('invalid type {} for vaction_requested'.format(type(v)))
            elif k == 'vaction_verified':
                if type(v) == int:
                    vaction_verified = np.datetime64(v, 'ns')
                else:
                    raise ValueError('invalid type {} for vaction_verified'.format(type(v)))
            elif k == 'market_url':
                market_url = str(v)
            elif k == 'market_realm':
                market_realm = str(v)
            elif k == 'ethkey':
                ethkey = binascii.a2b_hex(v[2:])
                print('88888888888888', ethkey)
            elif k == 'cskey':
                cskey = binascii.a2b_hex(v[2:])
            elif k == 'username':
                username = str(v)
            elif k == 'email':
                email = str(v)
            elif k == 'infura_network':
                infura_network = str(v)
            elif k == 'infura_key':
                infura_key = str(v)
            elif k == 'infura_secret':
                infura_secret = str(v)
            elif k == 'infura_url':
                infura_url = str(v)
            else:
                # skip unknown attribute
                print('unprocessed config attribute "{}"'.format(k))

        return Profile(path, name, ethkey, cskey, username, email, network_url, network_realm,
                       vaction_oid, vaction_requested, vaction_verified, market_url, market_realm,
                       infura_url, infura_network, infura_key, infura_secret)


class UserConfig(object):
    """
    nacl.bindings.crypto_secretbox

    :cvar KEY_SIZE: The size that the key is required to be.
    :cvar NONCE_SIZE: The size that the nonce is required to be.
    :cvar MACBYTES: The size of the authentication MAC tag in bytes.

    XSalsa20

    https://libsodium.gitbook.io/doc/advanced/stream_ciphers/xsalsa20
    256 bits keys, 192 bits nonces

    Encryption XSalsa20 stream cipher
    Authentication Poly1305 MAC
    """

    def __init__(self, config_path):
        from txaio import make_logger
        self.log = make_logger()
        self._config_path = os.path.abspath(config_path)
        self._profiles = {}

    @property
    def config_path(self) -> List[str]:
        return self._config_path

    @property
    def profiles(self) -> Dict[str, object]:
        return self._profiles

    def save(self, password: Optional[str] = None):
        """

        :param password:
        :return:
        """
        config = configparser.ConfigParser()
        for profile_name, profile in self._profiles.items():
            if profile_name not in config.sections():
                config.add_section(profile_name)
            pd = profile.marshal()
            from pprint import pprint
            pprint(pd)
            for option, value in pd.items():
                print('SET', profile_name, option, value)
                config.set(profile_name, option, value)

        with io.StringIO() as fp1:
            config.write(fp1)
        config_data = str(config).encode('utf8')

        if password:
            # binary file format header (64 bytes):
            #
            # * 8 bytes: 0xdeadbeef 0x00000666 magic number (big endian)
            # * 4 bytes: 0x00000001 encryption type 1 for "argon2id"
            # * 4 bytes data length (big endian)
            # * 8 bytes created timestamp ns (big endian)
            # * 8 bytes unused (filled 0x00 currently)
            # * 16 bytes salt
            #
            salt = os.urandom(16)
            context = 'xbrnetwork-config'
            priv_key = pkm_from_argon2_secret(email='', password=password, context=context, salt=salt)
            box = nacl.secret.SecretBox(priv_key)
            config_data_ciphertext = box.encrypt(config_data)
            dl = [
                b'\xde\xad\xbe\xef',
                b'\x00\x00\x06\x66',
                b'\x00\x00\x00\x01',
                struct.pack('>L', len(config_data_ciphertext)),
                struct.pack('>Q', time_ns()),
                b'\x00' * 8,
                salt,
                config_data_ciphertext,
            ]
            data = b''.join(dl)
        else:
            data = config_data

        with open(self._config_path, 'wb') as fp2:
            fp2.write(data)

        return len(data)

    def load(self, cb_get_password=None):
        if not os.path.exists(self._config_path) or not os.path.isfile(self._config_path):
            raise RuntimeError('config path "{}" cannot be loaded: so such file'.format(self._config_path))

        with open(self._config_path, 'rb') as fp:
            data = fp.read()

        if len(data) >= 64 and data[:8] == b'\xde\xad\xbe\xef\x00\x00\x06\x66':
            # binary format detected
            header = data[:64]
            body = data[64:]

            algo = struct.unpack('>L', header[8:12])[0]
            data_len = struct.unpack('>L', header[12:16])[0]
            created = struct.unpack('>Q', header[16:24])[0]

            print('algo', algo)
            print('data_len', data_len)
            print('created', created)

            assert algo in [0, 1]
            assert data_len == len(body)
            assert created < time_ns()

            created_ts = np.datetime64(created, 'ns')

        else:
            header = None
            body = data

        config = configparser.ConfigParser()
        config.read_string(body.decode('utf8'))

        profiles = {}
        for profile_name in config.sections():
            from pprint import pprint
            citems = config.items(profile_name)
            print('>>>>>>>>>>>>')
            pprint(citems)
            profile = Profile.parse(self._config_path, profile_name, citems)
            profiles[profile_name] = profile
            pprint(profile_name)
            pprint(profile)
        self._profiles = profiles

        self.log.debug('profiles loaded: {profiles}',
                       func=hltype(self.__init__),
                       profiles=', '.join(hlval(x) for x in sorted(self.profiles.keys())))


if 'CROSSBAR_FABRIC_URL' in os.environ:
    _DEFAULT_CFC_URL = os.environ['CROSSBAR_FABRIC_URL']
else:
    _DEFAULT_CFC_URL = u'wss://master.xbr.network/ws'


def style_error(text):
    if _HAS_COLOR_TERM:
        return click.style(text, fg='red', bold=True)
    else:
        return text


def style_ok(text):
    if _HAS_COLOR_TERM:
        return click.style(text, fg='green', bold=True)
    else:
        return text


class WampUrl(click.ParamType):
    """
    WAMP transport URL validator.
    """

    name = 'WAMP transport URL'

    def __init__(self):
        click.ParamType.__init__(self)

    def convert(self, value, param, ctx):
        try:
            parse_url(value)
        except Exception as e:
            self.fail(style_error(str(e)))
        else:
            return value


def prompt_for_wamp_url(msg, default=None):
    """
    Prompt user for WAMP transport URL (eg "wss://planet.xbr.network/ws").
    """
    value = click.prompt(msg, type=WampUrl(), default=default)
    return value


class EthereumAddress(click.ParamType):
    """
    Ethereum address validator.
    """

    name = 'Ethereum address'

    def __init__(self):
        click.ParamType.__init__(self)

    def convert(self, value, param, ctx):
        try:
            value = web3.Web3.toChecksumAddress(value)
            adr = binascii.a2b_hex(value[2:])
            if len(value) != 20:
                raise ValueError('Ethereum addres must be 20 bytes (160 bit), but was {} bytes'.format(len(adr)))
        except Exception as e:
            self.fail(style_error(str(e)))
        else:
            return value


def prompt_for_ethereum_address(msg):
    """
    Prompt user for an Ethereum (public) address.
    """
    value = click.prompt(msg, type=EthereumAddress())
    return value


class PrivateKey(click.ParamType):
    """
    Private key (32 bytes in HEX) validator.
    """

    name = 'Private key'

    def __init__(self, key_len):
        click.ParamType.__init__(self)
        self._key_len = key_len

    def convert(self, value, param, ctx):
        try:
            value = hexstr_if_str(to_hex, value)
            if value[:2] in ['0x', '\\x']:
                key = binascii.a2b_hex(value[2:])
            else:
                key = binascii.a2b_hex(value)
            if len(key) != self._key_len:
                raise ValueError('key length must be {} bytes, but was {} bytes'.format(self._key_len, len(key)))
        except Exception as e:
            self.fail(style_error(str(e)))
        else:
            return value


def prompt_for_key(msg, key_len, default=None):
    """
    Prompt user for a binary key of given length (in HEX).
    """
    value = click.prompt(msg, type=PrivateKey(key_len), default=default)
    return value


# default configuration stored in $HOME/.xbrnetwork/config.ini
_DEFAULT_CONFIG = """[default]
# username used with this profile
username={username}

# user email used with the profile (e.g. for verification emails)
email={email}

# XBR network node used as a directory server and gateway to XBR smart contracts
network_url={network_url}

# WAMP realm on network node, usually "xbrnetwork"
network_realm={network_realm}

# user private WAMP-cryptosign key (for client authentication)
cskey={cskey}

# user private Ethereum key (for signing transactions and e2e data encryption)
ethkey={ethkey}
"""

# # default XBR market URL to connect to
# market_url={market_url}
# market_realm={market_realm}
# # Infura blockchain gateway configuration
# infura_url={infura_url}
# infura_network={infura_network}
# infura_key={infura_key}
# infura_secret={infura_secret}


def load_or_create_profile(dotdir=None, profile=None, default_url=None, default_realm=None, default_email=None, default_username=None):
    dotdir = dotdir or '~/.xbrnetwork'
    profile = profile or 'default'
    default_url = default_url or 'wss://planet.xbr.network/ws'
    default_realm = default_realm or 'xbrnetwork'

    config_dir = os.path.expanduser(dotdir)
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
        click.echo('created new local user directory {}'.format(style_ok(config_dir)))

    config_path = os.path.join(config_dir, 'config.ini')
    if not os.path.isfile(config_path):
        click.echo('creating new user profile "{}"'.format(style_ok(profile)))
        with open(config_path, 'w') as f:
            network_url = prompt_for_wamp_url('enter the WAMP router URL of the network directory node', default=default_url)
            network_realm = click.prompt('enter the WAMP realm to join on the network directory node', type=str, default=default_realm)
            cskey = prompt_for_key('your private WAMP client key', 32, default='0x' + binascii.b2a_hex(os.urandom(32)).decode())
            ethkey = prompt_for_key('your private Etherum key', 32, default='0x' + binascii.b2a_hex(os.urandom(32)).decode())
            email = click.prompt('user email used for with profile', type=str, default=default_email)
            username = click.prompt('user name used with this profile', type=str, default=default_username)
            f.write(_DEFAULT_CONFIG.format(network_url=network_url, network_realm=network_realm, ethkey=ethkey,
                                           cskey=cskey, email=email, username=username))
            click.echo('created new local user configuration {}'.format(style_ok(config_path)))

    config_obj = UserConfig(config_path)
    profile_obj = config_obj.profiles.get(profile, None)

    if not profile_obj:
        raise click.ClickException('no such profile: "{}"'.format(profile))

    return profile_obj
