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
        ip_ver = 4 if len(peer) == 2 else 6
        return "tcp{2}:{0}:{1}".format(peer[0], peer[1], ip_ver)
    elif isinstance(peer, str):
        return "unix:{0}".format(peer)
    else:
        return "?:{0}".format(peer)


def get_serializes():
    from autobahn.wamp import serializer

    serializers = ['CBORSerializer', 'MsgPackSerializer', 'UBJSONSerializer', 'JsonSerializer']
    serializers = list(filter(lambda x: x, map(lambda s: getattr(serializer, s) if hasattr(serializer, s)
                                               else None, serializers)))
    return serializers
