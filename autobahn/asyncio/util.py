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

from __future__ import absolute_import

__all = (
    'sleep',
    'peer2str',
    'transport_channel_id',
)


def transport_channel_id(transport, is_server, channel_id_type):
    """
    Application-layer user authentication protocols are vulnerable to generic
    credential forwarding attacks, where an authentication credential sent by
    a client C to a server M may then be used by M to impersonate C at another
    server S. To prevent such credential forwarding attacks, modern authentication
    protocols rely on channel bindings. For example, WAMP-cryptosign can use
    the tls-unique channel identifier provided by the TLS layer to strongly bind
    authentication credentials to the underlying channel, so that a credential
    received on one TLS channel cannot be forwarded on another.

    """
    if channel_id_type not in [u'tls-unique']:
        raise Exception("invalid channel ID type {}".format(channel_id_type))

    ssl_obj = transport.get_extra_info('ssl_object')
    if ssl_obj is None:
        return None

    if hasattr(ssl_obj, 'get_channel_binding'):
        return ssl_obj.get_channel_binding(cb_type='tls-unique')
    return None


def peer2str(peer):
    if isinstance(peer, tuple):
        ip_ver = 4 if len(peer) == 2 else 6
        return u"tcp{2}:{0}:{1}".format(peer[0], peer[1], ip_ver)
    elif isinstance(peer, str):
        return u"unix:{0}".format(peer)
    else:
        return u"?:{0}".format(peer)


def get_serializers():
    from autobahn.wamp import serializer

    serializers = ['CBORSerializer', 'MsgPackSerializer', 'UBJSONSerializer', 'JsonSerializer']
    serializers = list(filter(lambda x: x, map(lambda s: getattr(serializer, s) if hasattr(serializer, s)
                                               else None, serializers)))
    return serializers
