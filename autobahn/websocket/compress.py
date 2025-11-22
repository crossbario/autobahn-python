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

from autobahn.websocket.compress_base import (
    PerMessageCompress,
    PerMessageCompressOffer,
    PerMessageCompressOfferAccept,
    PerMessageCompressResponse,
    PerMessageCompressResponseAccept,
)
from autobahn.websocket.compress_deflate import (
    PerMessageDeflate,
    PerMessageDeflateMixin,
    PerMessageDeflateOffer,
    PerMessageDeflateOfferAccept,
    PerMessageDeflateResponse,
    PerMessageDeflateResponseAccept,
)

# this must be a list (not tuple), since we dynamically
# extend it ..
__all__ = [
    "PERMESSAGE_COMPRESSION_EXTENSION",
    "PerMessageCompress",
    "PerMessageCompressOffer",
    "PerMessageCompressOfferAccept",
    "PerMessageCompressResponse",
    "PerMessageCompressResponseAccept",
    "PerMessageDeflate",
    "PerMessageDeflateOffer",
    "PerMessageDeflateOfferAccept",
    "PerMessageDeflateResponse",
    "PerMessageDeflateResponseAccept",
]

# map of available compression extensions
PERMESSAGE_COMPRESSION_EXTENSION = {
    # class for 'permessage-deflate' is always available
    PerMessageDeflateMixin.EXTENSION_NAME: {
        "Offer": PerMessageDeflateOffer,
        "OfferAccept": PerMessageDeflateOfferAccept,
        "Response": PerMessageDeflateResponse,
        "ResponseAccept": PerMessageDeflateResponseAccept,
        "PMCE": PerMessageDeflate,
    }
}


# include 'permessage-bzip2' classes if bzip2 is available
try:
    import bz2
except ImportError:
    bz2 = None
else:
    from autobahn.websocket.compress_bzip2 import (
        PerMessageBzip2,
        PerMessageBzip2Mixin,
        PerMessageBzip2Offer,
        PerMessageBzip2OfferAccept,
        PerMessageBzip2Response,
        PerMessageBzip2ResponseAccept,
    )

    PMCE = {
        "Offer": PerMessageBzip2Offer,
        "OfferAccept": PerMessageBzip2OfferAccept,
        "Response": PerMessageBzip2Response,
        "ResponseAccept": PerMessageBzip2ResponseAccept,
        "PMCE": PerMessageBzip2,
    }
    PERMESSAGE_COMPRESSION_EXTENSION[PerMessageBzip2Mixin.EXTENSION_NAME] = PMCE

    __all__.extend(
        [
            "PerMessageBzip2",
            "PerMessageBzip2Offer",
            "PerMessageBzip2OfferAccept",
            "PerMessageBzip2Response",
            "PerMessageBzip2ResponseAccept",
        ]
    )


# include 'permessage-snappy' classes if Snappy is available
try:
    # noinspection PyPackageRequirements
    import snappy
except ImportError:
    snappy = None
else:
    from autobahn.websocket.compress_snappy import (
        PerMessageSnappy,
        PerMessageSnappyMixin,
        PerMessageSnappyOffer,
        PerMessageSnappyOfferAccept,
        PerMessageSnappyResponse,
        PerMessageSnappyResponseAccept,
    )

    PMCE = {
        "Offer": PerMessageSnappyOffer,
        "OfferAccept": PerMessageSnappyOfferAccept,
        "Response": PerMessageSnappyResponse,
        "ResponseAccept": PerMessageSnappyResponseAccept,
        "PMCE": PerMessageSnappy,
    }
    PERMESSAGE_COMPRESSION_EXTENSION[PerMessageSnappyMixin.EXTENSION_NAME] = PMCE

    __all__.extend(
        [
            "PerMessageSnappy",
            "PerMessageSnappyOffer",
            "PerMessageSnappyOfferAccept",
            "PerMessageSnappyResponse",
            "PerMessageSnappyResponseAccept",
        ]
    )


# include 'permessage-brotli' classes if Brotli is available
# Use 'brotli' on CPython (CPyExt), 'brotlicffi' on PyPy (CFFI)
try:
    import platform

    if platform.python_implementation() == "PyPy":
        # noinspection PyPackageRequirements
        import brotlicffi as brotli
    else:
        # noinspection PyPackageRequirements
        import brotli
except ImportError:
    brotli = None
else:
    from autobahn.websocket.compress_brotli import (
        PerMessageBrotli,
        PerMessageBrotliMixin,
        PerMessageBrotliOffer,
        PerMessageBrotliOfferAccept,
        PerMessageBrotliResponse,
        PerMessageBrotliResponseAccept,
    )

    PMCE = {
        "Offer": PerMessageBrotliOffer,
        "OfferAccept": PerMessageBrotliOfferAccept,
        "Response": PerMessageBrotliResponse,
        "ResponseAccept": PerMessageBrotliResponseAccept,
        "PMCE": PerMessageBrotli,
    }
    PERMESSAGE_COMPRESSION_EXTENSION[PerMessageBrotliMixin.EXTENSION_NAME] = PMCE

    __all__.extend(
        [
            "PerMessageBrotli",
            "PerMessageBrotliOffer",
            "PerMessageBrotliOfferAccept",
            "PerMessageBrotliResponse",
            "PerMessageBrotliResponseAccept",
        ]
    )
