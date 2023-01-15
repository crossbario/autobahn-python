###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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
    User profile, stored as named section in ``${HOME}/.xbrnetwork/config.ini``:

    .. code-block:: INI

        [default]
        # username used with this profile
        username=joedoe

        # user email used with the profile (e.g. for verification emails)
        email=joe.doe@example.com

        # XBR network node used as a directory server and gateway to XBR smart contracts
        network_url=ws://localhost:8090/ws

        # WAMP realm on network node, usually "xbrnetwork"
        network_realm=xbrnetwork

        # user private WAMP-cryptosign key (for client authentication)
        cskey=0xb18bbe88ca0e189689e99f87b19addfb179d46aab3d59ec5d93a15286b949eb6

        # user private Ethereum key (for signing transactions and e2e data encryption)
        ethkey=0xfbada363e724d4db2faa2eeaa7d7aca37637b1076dd8cf6fefde13983abaa2ef
    """

    def __init__(self,
                 path: Optional[str] = None,
                 name: Optional[str] = None,
                 member_adr: Optional[str] = None,
                 ethkey: Optional[bytes] = None,
                 cskey: Optional[bytes] = None,
                 username: Optional[str] = None,
                 email: Optional[str] = None,
                 network_url: Optional[str] = None,
                 network_realm: Optional[str] = None,
                 member_oid: Optional[uuid.UUID] = None,
                 vaction_oid: Optional[uuid.UUID] = None,
                 vaction_requested: Optional[np.datetime64] = None,
                 vaction_verified: Optional[np.datetime64] = None,
                 data_url: Optional[str] = None,
                 data_realm: Optional[str] = None,
                 infura_url: Optional[str] = None,
                 infura_network: Optional[str] = None,
                 infura_key: Optional[str] = None,
                 infura_secret: Optional[str] = None):
        """

        :param path:
        :param name:
        :param member_adr:
        :param ethkey:
        :param cskey:
        :param username:
        :param email:
        :param network_url:
        :param network_realm:
        :param member_oid:
        :param vaction_oid:
        :param vaction_requested:
        :param vaction_verified:
        :param data_url:
        :param data_realm:
        :param infura_url:
        :param infura_network:
        :param infura_key:
        :param infura_secret:
        """
        from txaio import make_logger
        self.log = make_logger()

        self.path = path
        self.name = name

        self.member_adr = member_adr
        self.ethkey = ethkey
        self.cskey = cskey
        self.username = username
        self.email = email
        self.network_url = network_url
        self.network_realm = network_realm
        self.member_oid = member_oid
        self.vaction_oid = vaction_oid
        self.vaction_requested = vaction_requested
        self.vaction_verified = vaction_verified
        self.data_url = data_url
        self.data_realm = data_realm
        self.infura_url = infura_url
        self.infura_network = infura_network
        self.infura_key = infura_key
        self.infura_secret = infura_secret

    def marshal(self):
        obj = {}
        obj['member_adr'] = self.member_adr or ''
        obj['ethkey'] = '0x{}'.format(binascii.b2a_hex(self.ethkey).decode()) if self.ethkey else ''
        obj['cskey'] = '0x{}'.format(binascii.b2a_hex(self.cskey).decode()) if self.cskey else ''
        obj['username'] = self.username or ''
        obj['email'] = self.email or ''
        obj['network_url'] = self.network_url or ''
        obj['network_realm'] = self.network_realm or ''
        obj['member_oid'] = str(self.member_oid) if self.member_oid else ''
        obj['vaction_oid'] = str(self.vaction_oid) if self.vaction_oid else ''
        obj['vaction_requested'] = str(self.vaction_requested) if self.vaction_requested else ''
        obj['vaction_verified'] = str(self.vaction_verified) if self.vaction_verified else ''
        obj['data_url'] = self.data_url or ''
        obj['data_realm'] = self.data_realm or ''
        obj['infura_url'] = self.infura_url or ''
        obj['infura_network'] = self.infura_network or ''
        obj['infura_key'] = self.infura_key or ''
        obj['infura_secret'] = self.infura_secret or ''
        return obj

    @staticmethod
    def parse(path, name, items):
        member_adr = None
        ethkey = None
        cskey = None
        username = None
        email = None
        network_url = None
        network_realm = None
        member_oid = None
        vaction_oid = None
        vaction_requested = None
        vaction_verified = None
        data_url = None
        data_realm = None
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
                if type(v) == str and v != '':
                    vaction_oid = uuid.UUID(v)
                else:
                    vaction_oid = None
            elif k == 'member_adr':
                if type(v) == str and v != '':
                    member_adr = v
                else:
                    member_adr = None
            elif k == 'member_oid':
                if type(v) == str and v != '':
                    member_oid = uuid.UUID(v)
                else:
                    member_oid = None
            elif k == 'vaction_requested':
                if type(v) == int and v:
                    vaction_requested = np.datetime64(v, 'ns')
                else:
                    vaction_requested = v
            elif k == 'vaction_verified':
                if type(v) == int:
                    vaction_verified = np.datetime64(v, 'ns')
                else:
                    vaction_verified = v
            elif k == 'data_url':
                data_url = str(v)
            elif k == 'data_realm':
                data_realm = str(v)
            elif k == 'ethkey':
                ethkey = binascii.a2b_hex(v[2:])
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
            elif k in ['path', 'name']:
                pass
            else:
                # skip unknown attribute
                print('unprocessed config attribute "{}"'.format(k))

        return Profile(path, name,
                       member_adr, ethkey, cskey,
                       username, email,
                       network_url, network_realm,
                       member_oid,
                       vaction_oid, vaction_requested, vaction_verified,
                       data_url, data_realm,
                       infura_url, infura_network, infura_key, infura_secret)


class UserConfig(object):
    """
    Local user configuration file. The data is either a plain text (unencrypted)
    .ini file, or such a file encrypted with XSalsa20-Poly1305, and with a
    binary file header of 48 octets.
    """
    def __init__(self, config_path):
        """

        :param config_path: The user configuration file path.
        """
        from txaio import make_logger
        self.log = make_logger()
        self._config_path = os.path.abspath(config_path)
        self._profiles = {}

    @property
    def config_path(self) -> List[str]:
        """
        Return the path to the user configuration file exposed by this object.,

        :return: Local filesystem path.
        """
        return self._config_path

    @property
    def profiles(self) -> Dict[str, object]:
        """
        Access to a map of user profiles in this user configuration.

        :return: Map of user profiles.
        """
        return self._profiles

    def save(self, password: Optional[str] = None):
        """
        Save this user configuration to the underlying configuration file. The user
        configuration file can be encrypted using Argon2id when a ``password`` is given.

        :param password: The optional Argon2id password.

        :return: Number of octets written to the user configuration file.
        """
        written = 0
        config = configparser.ConfigParser()
        for profile_name, profile in self._profiles.items():
            if profile_name not in config.sections():
                config.add_section(profile_name)
                written += 1
            pd = profile.marshal()
            for option, value in pd.items():
                config.set(profile_name, option, value)

        with io.StringIO() as fp1:
            config.write(fp1)
            config_data = fp1.getvalue().encode('utf8')

        if password:
            # binary file format header (48 bytes):
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

        self.log.debug('configuration with {sections} sections, {bytes_written} bytes written to {written_to}',
                       sections=written, bytes_written=len(data), written_to=self._config_path)

        return len(data)

    def load(self, cb_get_password=None) -> List[str]:
        """
        Load this object from the underlying user configuration file. When the
        file is encrypted, call back into ``cb_get_password`` to get the user password.

        :param cb_get_password: Callback called when password is needed.

        :return: List of profiles loaded.
        """
        if not os.path.exists(self._config_path) or not os.path.isfile(self._config_path):
            raise RuntimeError('config path "{}" cannot be loaded: so such file'.format(self._config_path))

        with open(self._config_path, 'rb') as fp:
            data = fp.read()

        if len(data) >= 48 and data[:8] == b'\xde\xad\xbe\xef\x00\x00\x06\x66':
            # binary format detected
            header = data[:48]
            body = data[48:]

            algo = struct.unpack('>L', header[8:12])[0]
            data_len = struct.unpack('>L', header[12:16])[0]
            created = struct.unpack('>Q', header[16:24])[0]
            # created_ts = np.datetime64(created, 'ns')

            assert algo in [0, 1]
            assert data_len == len(body)
            assert created < time_ns()

            salt = header[32:48]
            context = 'xbrnetwork-config'
            if cb_get_password:
                password = cb_get_password()
            else:
                password = ''
            priv_key = pkm_from_argon2_secret(email='', password=password, context=context, salt=salt)
            box = nacl.secret.SecretBox(priv_key)
            body = box.decrypt(body)

        else:
            header = None
            body = data

        config = configparser.ConfigParser()
        config.read_string(body.decode('utf8'))

        profiles = {}
        for profile_name in config.sections():
            citems = config.items(profile_name)
            profile = Profile.parse(self._config_path, profile_name, citems)
            profiles[profile_name] = profile
        self._profiles = profiles

        loaded_profiles = sorted(self.profiles.keys())
        return loaded_profiles


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
    config_obj.load()
    profile_obj = config_obj.profiles.get(profile, None)

    if not profile_obj:
        raise click.ClickException('no such profile: "{}"'.format(profile))

    return profile_obj
