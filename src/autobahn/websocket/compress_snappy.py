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

import snappy

from autobahn.exception import PayloadCorruptError, PayloadExceededError
from autobahn.websocket.compress_base import (
    PerMessageCompress,
    PerMessageCompressOffer,
    PerMessageCompressOfferAccept,
    PerMessageCompressResponse,
    PerMessageCompressResponseAccept,
)

# Snappy framing format: a stream identifier chunk (type 0xff) has length 6,
# a data chunk (type 0x00 compressed, 0x01 uncompressed) is at most
# 4 + 76490 octets long (CRC, plus the maximum compressed size of the 64 KiB
# a chunk may hold), and chunk types 0x02-0x7f are reserved, not skippable.
_SNAPPY_MAX_DATA_CHUNK_LENGTH = 4 + 76490

__all__ = (
    "PerMessageSnappy",
    "PerMessageSnappyMixin",
    "PerMessageSnappyOffer",
    "PerMessageSnappyOfferAccept",
    "PerMessageSnappyResponse",
    "PerMessageSnappyResponseAccept",
)


class PerMessageSnappyMixin:
    """
    Mixin class for this extension.
    """

    EXTENSION_NAME = "permessage-snappy"
    """
    Name of this WebSocket extension.
    """


class PerMessageSnappyOffer(PerMessageCompressOffer, PerMessageSnappyMixin):
    """
    Set of extension parameters for `permessage-snappy` WebSocket extension
    offered by a client to a server.
    """

    @classmethod
    def parse(cls, params):
        """
        Parses a WebSocket extension offer for `permessage-snappy` provided by a client to a server.

        :param params: Output from :func:`autobahn.websocket.WebSocketProtocol._parseExtensionsHeader`.
        :type params: list

        :returns: A new instance of :class:`autobahn.compress.PerMessageSnappyOffer`.
        :rtype: obj
        """
        # extension parameter defaults
        accept_no_context_takeover = False
        request_no_context_takeover = False

        # verify/parse client ("client-to-server direction") parameters of permessage-snappy offer
        for p in params:
            if len(params[p]) > 1:
                raise Exception(
                    f"multiple occurrence of extension parameter '{p}' for extension '{cls.EXTENSION_NAME}'"
                )

            val = params[p][0]

            if p == "client_no_context_takeover":
                # noinspection PySimplifyBooleanCheck
                if val is not True:
                    raise Exception(
                        f"illegal extension parameter value '{val}' for parameter '{p}' of extension '{cls.EXTENSION_NAME}'"
                    )
                else:
                    accept_no_context_takeover = True

            elif p == "server_no_context_takeover":
                # noinspection PySimplifyBooleanCheck
                if val is not True:
                    raise Exception(
                        f"illegal extension parameter value '{val}' for parameter '{p}' of extension '{cls.EXTENSION_NAME}'"
                    )
                else:
                    request_no_context_takeover = True

            else:
                raise Exception(
                    f"illegal extension parameter '{p}' for extension '{cls.EXTENSION_NAME}'"
                )

        offer = cls(accept_no_context_takeover, request_no_context_takeover)
        return offer

    def __init__(
        self, accept_no_context_takeover=True, request_no_context_takeover=False
    ):
        """

        :param accept_no_context_takeover: Iff true, client accepts "no context takeover" feature.
        :type accept_no_context_takeover: bool
        :param request_no_context_takeover: Iff true, client request "no context takeover" feature.
        :type request_no_context_takeover: bool
        """
        if type(accept_no_context_takeover) != bool:
            raise Exception(
                f"invalid type {type(accept_no_context_takeover)} for accept_no_context_takeover"
            )

        self.accept_no_context_takeover = accept_no_context_takeover

        if type(request_no_context_takeover) != bool:
            raise Exception(
                f"invalid type {type(request_no_context_takeover)} for request_no_context_takeover"
            )

        self.request_no_context_takeover = request_no_context_takeover

    def get_extension_string(self):
        """
        Returns the WebSocket extension configuration string as sent to the server.

        :returns: PMCE configuration string.
        :rtype: str
        """
        pmce_string = self.EXTENSION_NAME
        if self.accept_no_context_takeover:
            pmce_string += "; client_no_context_takeover"
        if self.request_no_context_takeover:
            pmce_string += "; server_no_context_takeover"
        return pmce_string

    def __json__(self):
        """
        Returns a JSON serializable object representation.

        :returns: JSON serializable representation.
        :rtype: dict
        """
        return {
            "extension": self.EXTENSION_NAME,
            "accept_no_context_takeover": self.accept_no_context_takeover,
            "request_no_context_takeover": self.request_no_context_takeover,
        }

    def __repr__(self):
        """
        Returns Python object representation that can be eval'ed to reconstruct the object.

        :returns: Python string representation.
        :rtype: str
        """
        return (
            f"PerMessageSnappyOffer(accept_no_context_takeover = {self.accept_no_context_takeover}, request_no_context_takeover = {self.request_no_context_takeover})"
        )


class PerMessageSnappyOfferAccept(PerMessageCompressOfferAccept, PerMessageSnappyMixin):
    """
    Set of parameters with which to accept an `permessage-snappy` offer
    from a client by a server.
    """

    def __init__(
        self, offer, request_no_context_takeover=False, no_context_takeover=None
    ):
        """

        :param offer: The offer being accepted.
        :type offer: Instance of :class:`autobahn.compress.PerMessageSnappyOffer`.
        :param request_no_context_takeover: Iff true, server request "no context takeover" feature.
        :type request_no_context_takeover: bool
        :param no_context_takeover: Override server ("server-to-client direction") context takeover (this must be compatible with offer).
        :type no_context_takeover: bool
        """
        if not isinstance(offer, PerMessageSnappyOffer):
            raise Exception(f"invalid type {type(offer)} for offer")

        self.offer = offer

        if type(request_no_context_takeover) != bool:
            raise Exception(
                f"invalid type {type(request_no_context_takeover)} for request_no_context_takeover"
            )

        if request_no_context_takeover and not offer.accept_no_context_takeover:
            raise Exception(
                f"invalid value {request_no_context_takeover} for request_no_context_takeover - feature unsupported by client"
            )

        self.request_no_context_takeover = request_no_context_takeover

        if no_context_takeover is not None:
            if type(no_context_takeover) != bool:
                raise Exception(
                    f"invalid type {type(no_context_takeover)} for no_context_takeover"
                )

            if offer.request_no_context_takeover and not no_context_takeover:
                raise Exception(
                    f"invalid value {no_context_takeover} for no_context_takeover - client requested feature"
                )

        self.no_context_takeover = no_context_takeover

    def get_extension_string(self):
        """
        Returns the WebSocket extension configuration string as sent to the server.

        :returns: PMCE configuration string.
        :rtype: str
        """
        pmce_string = self.EXTENSION_NAME
        if self.offer.request_no_context_takeover:
            pmce_string += "; server_no_context_takeover"
        if self.request_no_context_takeover:
            pmce_string += "; client_no_context_takeover"
        return pmce_string

    def __json__(self):
        """
        Returns a JSON serializable object representation.

        :returns: JSON serializable representation.
        :rtype: dict
        """
        return {
            "extension": self.EXTENSION_NAME,
            "offer": self.offer.__json__(),
            "request_no_context_takeover": self.request_no_context_takeover,
            "no_context_takeover": self.no_context_takeover,
        }

    def __repr__(self):
        """
        Returns Python object representation that can be eval'ed to reconstruct the object.

        :returns: Python string representation.
        :rtype: str
        """
        return (
            f"PerMessageSnappyAccept(offer = {self.offer.__repr__()}, request_no_context_takeover = {self.request_no_context_takeover}, no_context_takeover = {self.no_context_takeover})"
        )


class PerMessageSnappyResponse(PerMessageCompressResponse, PerMessageSnappyMixin):
    """
    Set of parameters for `permessage-snappy` responded by server.
    """

    @classmethod
    def parse(cls, params):
        """
        Parses a WebSocket extension response for `permessage-snappy` provided by a server to a client.

        :param params: Output from :func:`autobahn.websocket.WebSocketProtocol._parseExtensionsHeader`.
        :type params: list

        :returns: A new instance of :class:`autobahn.compress.PerMessageSnappyResponse`.
        :rtype: obj
        """
        client_no_context_takeover = False
        server_no_context_takeover = False

        for p in params:
            if len(params[p]) > 1:
                raise Exception(
                    f"multiple occurrence of extension parameter '{p}' for extension '{cls.EXTENSION_NAME}'"
                )

            val = params[p][0]

            if p == "client_no_context_takeover":
                # noinspection PySimplifyBooleanCheck
                if val is not True:
                    raise Exception(
                        f"illegal extension parameter value '{val}' for parameter '{p}' of extension '{cls.EXTENSION_NAME}'"
                    )
                else:
                    client_no_context_takeover = True

            elif p == "server_no_context_takeover":
                # noinspection PySimplifyBooleanCheck
                if val is not True:
                    raise Exception(
                        f"illegal extension parameter value '{val}' for parameter '{p}' of extension '{cls.EXTENSION_NAME}'"
                    )
                else:
                    server_no_context_takeover = True

            else:
                raise Exception(
                    f"illegal extension parameter '{p}' for extension '{cls.EXTENSION_NAME}'"
                )

        response = cls(client_no_context_takeover, server_no_context_takeover)
        return response

    def __init__(self, client_no_context_takeover, server_no_context_takeover):
        self.client_no_context_takeover = client_no_context_takeover
        self.server_no_context_takeover = server_no_context_takeover

    def __json__(self):
        """
        Returns a JSON serializable object representation.

        :returns: JSON serializable representation.
        :rtype: dict
        """
        return {
            "extension": self.EXTENSION_NAME,
            "client_no_context_takeover": self.client_no_context_takeover,
            "server_no_context_takeover": self.server_no_context_takeover,
        }

    def __repr__(self):
        """
        Returns Python object representation that can be eval'ed to reconstruct the object.

        :returns: Python string representation.
        :rtype: str
        """
        return (
            f"PerMessageSnappyResponse(client_no_context_takeover = {self.client_no_context_takeover}, server_no_context_takeover = {self.server_no_context_takeover})"
        )


class PerMessageSnappyResponseAccept(
    PerMessageCompressResponseAccept, PerMessageSnappyMixin
):
    """
    Set of parameters with which to accept an `permessage-snappy` response
    from a server by a client.
    """

    def __init__(self, response, no_context_takeover=None):
        """

        :param response: The response being accepted.
        :type response: Instance of :class:`autobahn.compress.PerMessageSnappyResponse`.
        :param no_context_takeover: Override client ("client-to-server direction") context takeover (this must be compatible with response).
        :type no_context_takeover: bool
        """
        if not isinstance(response, PerMessageSnappyResponse):
            raise Exception(f"invalid type {type(response)} for response")

        self.response = response

        if no_context_takeover is not None:
            if type(no_context_takeover) != bool:
                raise Exception(
                    f"invalid type {type(no_context_takeover)} for no_context_takeover"
                )

            if response.client_no_context_takeover and not no_context_takeover:
                raise Exception(
                    f"invalid value {no_context_takeover} for no_context_takeover - server requested feature"
                )

        self.no_context_takeover = no_context_takeover

    def __json__(self):
        """
        Returns a JSON serializable object representation.

        :returns: JSON serializable representation.
        :rtype: dict
        """
        return {
            "extension": self.EXTENSION_NAME,
            "response": self.response.__json__(),
            "no_context_takeover": self.no_context_takeover,
        }

    def __repr__(self):
        """
        Returns Python object representation that can be eval'ed to reconstruct the object.

        :returns: Python string representation.
        :rtype: str
        """
        return (
            f"PerMessageSnappyResponseAccept(response = {self.response.__repr__()}, no_context_takeover = {self.no_context_takeover})"
        )


class PerMessageSnappy(PerMessageCompress, PerMessageSnappyMixin):
    """
    `permessage-snappy` WebSocket extension processor.
    """

    @classmethod
    def create_from_response_accept(cls, is_server, accept):
        pmce = cls(
            is_server,
            accept.response.server_no_context_takeover,
            (
                accept.no_context_takeover
                if accept.no_context_takeover is not None
                else accept.response.client_no_context_takeover
            ),
        )
        return pmce

    @classmethod
    def create_from_offer_accept(cls, is_server, accept):
        pmce = cls(
            is_server,
            (
                accept.no_context_takeover
                if accept.no_context_takeover is not None
                else accept.offer.request_no_context_takeover
            ),
            accept.request_no_context_takeover,
        )
        return pmce

    def __init__(
        self, is_server, server_no_context_takeover, client_no_context_takeover
    ):
        self._is_server = is_server
        self.server_no_context_takeover = server_no_context_takeover
        self.client_no_context_takeover = client_no_context_takeover

        self._compressor = None
        self._decompressor = None
        # received input not yet fed to the decompressor (an incomplete chunk)
        self._decompress_pending = bytearray()

    def __json__(self):
        return {
            "extension": self.EXTENSION_NAME,
            "server_no_context_takeover": self.server_no_context_takeover,
            "client_no_context_takeover": self.client_no_context_takeover,
        }

    def __repr__(self):
        return (
            f"PerMessageSnappy(is_server = {self._is_server}, server_no_context_takeover = {self.server_no_context_takeover}, client_no_context_takeover = {self.client_no_context_takeover})"
        )

    def start_compress_message(self):
        if self._is_server:
            if self._compressor is None or self.server_no_context_takeover:
                self._compressor = snappy.StreamCompressor()
        else:
            if self._compressor is None or self.client_no_context_takeover:
                self._compressor = snappy.StreamCompressor()

    def compress_message_data(self, data):
        return self._compressor.add_chunk(data)

    def end_compress_message(self):
        return b""

    def start_decompress_message(self):
        if self._is_server:
            if self._decompressor is None or self.client_no_context_takeover:
                self._decompressor = snappy.StreamDecompressor()
                self._decompress_pending = bytearray()
        else:
            if self._decompressor is None or self.server_no_context_takeover:
                self._decompressor = snappy.StreamDecompressor()
                self._decompress_pending = bytearray()

    def decompress_message_data(self, data, max_output_len=None):
        # python-snappy's StreamDecompressor has no output-length argument, so
        # it is fed one framing chunk (4-octet header: type, 24-bit length) at
        # a time. A chunk decompresses to at most 64 KiB (the decoder rejects
        # larger ones), so decompression stops within 64 KiB of the budget,
        # instead of inflating the whole frame first.
        # (A bytearray, so input trickling in over many calls is appended,
        # not copied anew each time.)
        buf = self._decompress_pending
        buf += data
        pos = 0
        out = []
        size = 0
        while len(buf) - pos >= 4:
            kind = buf[pos]
            length = int.from_bytes(buf[pos + 1 : pos + 4], "little")
            # reject a bad chunk header right away, instead of buffering a
            # chunk that cannot be valid
            if (
                (kind == 0xFF and length != 6)
                or (kind <= 0x01 and length > _SNAPPY_MAX_DATA_CHUNK_LENGTH)
                or 0x02 <= kind <= 0x7F
            ):
                raise PayloadCorruptError(
                    "invalid permessage-snappy data: bad chunk header "
                    f"(type 0x{kind:02x}, length {length})"
                )
            end = pos + 4 + length
            if end > len(buf):
                break
            try:
                chunk = self._decompressor.decompress(bytes(buf[pos:end]))
            except (OSError, snappy.UncompressError) as e:
                raise PayloadCorruptError(f"invalid permessage-snappy data: {e}") from e
            pos = end
            size += len(chunk)
            if max_output_len is not None and size > max_output_len:
                raise PayloadExceededError(
                    "WebSocket message exceeds decompression limit of "
                    f"{max_output_len} octets"
                )
            out.append(chunk)
        del buf[:pos]
        return b"".join(out)

    def end_decompress_message(self):
        # A message ends on a chunk boundary: anything left over is a
        # truncated chunk, or not snappy framing at all.
        if self._decompress_pending:
            self._decompress_pending = bytearray()
            raise PayloadCorruptError("truncated permessage-snappy data")
