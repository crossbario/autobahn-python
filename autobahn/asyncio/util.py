import binascii
class _LazyHexFormatter(object):
    """
    This is used to avoid calling binascii.hexlify() on data given to
    log.debug() calls unless debug is active (for example). Like::

        self.log.debug(
            "Some data: {octets}",
            octets=_LazyHexFormatter(os.urandom(32)),
        )
    """
    __slots__ = ('obj',)

    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return binascii.hexlify(self.obj).decode('ascii')

def peer2str(peer):
    if isinstance(peer, tuple):
        ip_ver=4 if len(peer)==2 else 6
        return "tcp{2}:{0}:{1}".format(peer[0], peer[1], ip_ver)
    elif isinstance(peer, str):
        return "unix:{0}".format(peer)
    else:
        return "?:{0}".format(peer)
    
def get_serializes():
    from autobahn.wamp import serializer
    
    serializers=['CBORSerializer', 'MsgPackSerializer', 'UBJSONSerializer', 'JsonSerializer']
    serializers=list(filter(lambda x:x, map(lambda s: getattr(serializer, s) if hasattr(serializer,s) else None,
                                             serializers )))
    return serializers

#TODO - check and modify for asyncio transport    
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
    if channel_id_type is None:
        return None

    if channel_id_type not in [u'tls-unique']:
        raise Exception("invalid channel ID type {}".format(channel_id_type))

    if hasattr(transport, '_tlsConnection'):
        # Obtain latest TLS Finished message that we expected from peer, or None if handshake is not completed.
        # http://www.pyopenssl.org/en/stable/api/ssl.html#OpenSSL.SSL.Connection.get_peer_finished

        if is_server:
            # for routers (=servers), the channel ID is based on the TLS Finished message we
            # expected to receive from the client
            tls_finished_msg = transport._tlsConnection.get_peer_finished()
        else:
            # for clients, the channel ID is based on the TLS Finished message we sent
            # to the router (=server)
            tls_finished_msg = transport._tlsConnection.get_finished()

        m = hashlib.sha256()
        m.update(tls_finished_msg)
        return m.digest()

    else:
        return None
