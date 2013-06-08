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
           "PerMessageCompressAccept",
           "PerMessageCompressParams",
           "PerMessageDeflateOffer",
           "PerMessageDeflateAccept",
           "PerMessageDeflateParams",
           "PerMessageBzip2Offer",
           "PerMessageBzip2Accept",
           "PerMessageBzip2Params",
           ]


import zlib
import bz2



class PerMessageCompressOffer:
   """
   Base class for WebSocket compression parameter offers by the client.
   """
   pass



class PerMessageCompressAccept:
   """
   Base class for WebSocket compression parameter accepts by the server.
   """
   pass



class PerMessageCompressParams:
   """
   Base class for WebSocket compression negotiated parameters.
   """
   pass



class PerMessageDeflateOffer(PerMessageCompressOffer):
   """
   Set of parameters for permessage-deflate offered by client.
   """

   def __init__(self,
                acceptNoContextTakeover = True,
                acceptMaxWindowBits = True,
                requestNoContextTakeover = False,
                requestMaxWindowBits = 0):
      """
      Constructor.

      :param acceptNoContextTakeover: Iff true, client accepts "no context takeover" feature.
      :type acceptNoContextTakeover: bool
      :param acceptMaxWindowBits: Iff true, client accepts setting "max window size".
      :type acceptMaxWindowBits: bool
      :param requestNoContextTakeover: Iff true, client request "no context takeover" feature.
      :type requestNoContextTakeover: bool
      :param requestMaxWindowBits: Iff non-zero, client requests given "max window size" - must be 8-15.
      :type requestMaxWindowBits: int
      """
      self.acceptNoContextTakeover = acceptNoContextTakeover
      self.acceptMaxWindowBits = acceptMaxWindowBits
      self.requestNoContextTakeover = requestNoContextTakeover
      self.requestMaxWindowBits = requestMaxWindowBits

      e = 'permessage-deflate'
      if self.acceptNoContextTakeover:
         e += "; c2s_no_context_takeover"
      if self.acceptMaxWindowBits:
         e += "; c2s_max_window_bits"
      if self.requestNoContextTakeover:
         e += "; s2c_no_context_takeover"
      if self.requestMaxWindowBits != 0:
         e += "; s2c_max_window_bits=%d" % self.requestMaxWindowBits
      self._pmceString = e


   def getExtensionString(self):
      """
      Returns the WebSocket extension configuration string.
      """
      return self._pmceString


   def __json__(self):
      return {'acceptNoContextTakeover': self.acceptNoContextTakeover,
              'acceptMaxWindowBits': self.acceptMaxWindowBits,
              'requestNoContextTakeover': self.requestNoContextTakeover,
              'requestMaxWindowBits': self.requestMaxWindowBits}


   def __repr__(self):
      return "PerMessageDeflateOffer(acceptNoContextTakeover = %s, acceptMaxWindowBits = %s, requestNoContextTakeover = %s, requestMaxWindowBits = %s)" % (self.acceptNoContextTakeover, self.acceptMaxWindowBits, self.requestNoContextTakeover, self.requestMaxWindowBits)



class PerMessageDeflateAccept(PerMessageCompressAccept):
   """
   Set of parameters with which to accept an permessage-deflate offer
   from a client by a server.
   """

   def __init__(self,
                requestNoContextTakeover = False,
                requestMaxWindowBits = 0):
      self.requestNoContextTakeover = requestNoContextTakeover
      self.requestMaxWindowBits = requestMaxWindowBits


   def __json__(self):
      return {'requestNoContextTakeover': self.requestNoContextTakeover,
              'requestMaxWindowBits': self.requestMaxWindowBits}


   def __repr__(self):
      return "PerMessageDeflateAccept(requestNoContextTakeover = %s, requestMaxWindowBits = %s)" % (self.requestNoContextTakeover, self.requestMaxWindowBits)



class PerMessageDeflateParams(PerMessageCompressParams):
   """
   Negotiated parameters for permessage-deflate.
   """

   def __init__(self,
                s2c_no_context_takeover,
                c2s_no_context_takeover,
                s2c_max_window_bits,
                c2s_max_window_bits):

      self.s2c_no_context_takeover = s2c_no_context_takeover
      self.c2s_no_context_takeover = c2s_no_context_takeover
      self.s2c_max_window_bits = s2c_max_window_bits if s2c_max_window_bits != 0 else zlib.MAX_WBITS
      self.c2s_max_window_bits = c2s_max_window_bits if c2s_max_window_bits != 0 else zlib.MAX_WBITS

      s = "permessage-deflate"
      if s2c_no_context_takeover:
         s += "; s2c_no_context_takeover"
      if s2c_max_window_bits != 0:
         s += "; s2c_max_window_bits=%d" % s2c_max_window_bits
      if c2s_no_context_takeover:
         s += "; c2s_no_context_takeover"
      if c2s_max_window_bits != 0:
         s += "; c2s_max_window_bits=%d" % c2s_max_window_bits
      self._pmceString = s


   def getExtensionString(self):
      return self._pmceString



class PerMessageBzip2Offer(PerMessageCompressOffer):
   """
   Set of parameters for permessage-bzip2 offered by client.
   """

   def __init__(self,
                acceptCompressLevel = True,
                requestCompressLevel = 0):
      """
      Constructor.

      :param acceptCompressLevel: Iff true, client accepts "compression level" feature.
      :type acceptCompressLevel: bool
      :param requestCompressLevel: Iff non-zero, client requests given "compression level" - must be 1-9.
      :type requestCompressLevel: int
      """
      self.acceptCompressLevel = acceptCompressLevel
      self.requestCompressLevel = requestCompressLevel

      e = 'permessage-bzip2'
      if self.acceptCompressLevel:
         e += "; c2s_compress_level"
      if self.requestCompressLevel != 0:
         e += "; s2c_compress_level=%d" % self.requestCompressLevel
      self._pmceString = e


   def getExtensionString(self):
      """
      Returns the WebSocket extension configuration string.
      """
      return self._pmceString


   def __json__(self):
      return {'acceptCompressLevel': self.acceptCompressLevel,
              'requestCompressLevel': self.requestCompressLevel}



class PerMessageBzip2Accept(PerMessageCompressAccept):
   """
   Set of parameters with which to accept an permessage-bzip2 offer
   from a client by a server.
   """

   def __init__(self,
                requestCompressLevel = 0):
      self.requestCompressLevel = requestCompressLevel


   def __json__(self):
      return {'requestCompressLevel': self.requestCompressLevel}


   def __repr__(self):
      return "PerMessageBzip2Accept(requestCompressLevel = %s)" % (self.requestCompressLevel,)



class PerMessageBzip2Params(PerMessageCompressParams):
   """
   Negotiated parameters for permessage-bzip2.
   """

   def __init__(self,
                s2c_compress_level,
                c2s_compress_level):

      self.s2c_compress_level = s2c_compress_level if s2c_compress_level != 0 else 9
      self.c2s_compress_level = c2s_compress_level if c2s_compress_level != 0 else 9

      s = "permessage-bzip2"
      if s2c_compress_level != 0:
         s += "; s2c_compress_level=%d" % s2c_compress_level
      if c2s_compress_level != 0:
         s += "; c2s_compress_level=%d" % c2s_compress_level
      self._pmceString = s


   def getExtensionString(self):
      return self._pmceString
