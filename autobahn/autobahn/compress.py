###############################################################################
##
##  Copyright 2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

__all__ = ["PerMessageCompressOffer",
           "PerMessageCompressResponse",
           "PerMessageCompressAccept",
           "PerMessageCompress",

           "PerMessageDeflateOffer",
           "PerMessageDeflateResponse",
           "PerMessageDeflateAccept",
           "PerMessageDeflate",

           "PerMessageBzip2Offer",
           "PerMessageBzip2Response",
           "PerMessageBzip2Accept",
           "PerMessageBzip2",

           "PERMESSAGE_COMPRESSION_EXTENSION"
           ]


from compress_base import *
from compress_deflate import *
from compress_bzip2 import *


## class for "permessage-deflate" and "permessage-bzip2" are always available
##
PERMESSAGE_COMPRESSION_EXTENSION = {

   PerMessageDeflateMixin.EXTENSION_NAME: {
      'Offer': PerMessageDeflateOffer,
      'Response': PerMessageDeflateResponse,
      'Accept': PerMessageDeflateAccept,
      'PMCE': PerMessageDeflate},

   PerMessageBzip2Mixin.EXTENSION_NAME: {
      'Offer': PerMessageBzip2Offer,
      'Response': PerMessageBzip2Response,
      'Accept': PerMessageBzip2Accept,
      'PMCE': PerMessageBzip2}
}


## include "permessage-snappy" classes if Snappy is available
##
try:
   import snappy
   from compress_snappy import *
   PMCE = {
      'Offer': PerMessageSnappyOffer,
      'Response': PerMessageSnappyResponse,
      'Accept': PerMessageSnappyAccept,
      'PMCE': PerMessageSnappy
   }
   PERMESSAGE_COMPRESSION_EXTENSION[PerMessageSnappyMixin.EXTENSION_NAME] = PMCE

   __all__.extend(["PerMessageSnappyOffer",
                   "PerMessageSnappyResponse",
                   "PerMessageSnappyAccept",
                   "PerMessageSnappy"])

except ImportError:
   pass
