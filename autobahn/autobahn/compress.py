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
           "PerMessageDeflateAccept",
           "PerMessageDeflate",
           "PerMessageBzip2Offer",
           "PerMessageBzip2Response",
           "PerMessageBzip2Accept",
           "PerMessageBzip2",
           "PERMESSAGE_COMPRESSION_EXTENSION"
           ]


import zlib
import bz2


try:
   import snappy
except ImportError:
   pass


class PerMessageCompressOffer:
   """
   Base class for WebSocket compression parameter offers by the client.
   """
   pass



class PerMessageCompressResponse:
   """
   Base class for WebSocket compression parameter response by server.
   """
   pass



class PerMessageCompressAccept:
   """
   Base class for WebSocket compression parameter accepts by the server.
   """
   pass



class PerMessageCompress:
   """
   Base class for WebSocket compression negotiated parameters.
   """
   pass



class PerMessageDeflateMixin:

   EXTENSION_NAME = "permessage-deflate"



class PerMessageDeflateOffer(PerMessageCompressOffer, PerMessageDeflateMixin):
   """
   Set of parameters for permessage-deflate offered by client.
   """

   @classmethod
   def parse(Klass, params):
      """
      Parses a WebSocket extension offer for permessage-deflate provided by a client to a server.
      """

      ## extension parameter defaults
      ##
      acceptMaxWindowBits = False
      acceptNoContextTakeover = True
      #acceptNoContextTakeover = False # FIXME: this may change in draft
      requestMaxWindowBits = 0
      requestNoContextTakeover = False

      for p in params:

         if len(params[p]) > 1:
            raise Exception("multiple occurence of extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

         val = params[p][0]

         if p == 'c2s_max_window_bits':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               acceptMaxWindowBits = True

         elif p == 'c2s_no_context_takeover':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               acceptNoContextTakeover = True

         elif p == 's2c_max_window_bits':
            if val not in ['8', '9', '10', '11', '12', '13', '14', '15']:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               requestMaxWindowBits = int(val)

         elif p == 's2c_no_context_takeover':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               requestNoContextTakeover = True

         else:
            raise Exception("illegal extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

      offer = Klass(acceptNoContextTakeover,
                    acceptMaxWindowBits,
                    requestNoContextTakeover,
                    requestMaxWindowBits)
      return offer


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



class PerMessageDeflateResponse(PerMessageCompressResponse, PerMessageDeflateMixin):
   """
   Set of parameters for permessage-deflate responded by server.
   """

   @classmethod
   def parse(Klass, params):
      """
      Parses a WebSocket extension response for permessage-deflate provided by a server to a client.
      """
      c2s_max_window_bits = 0
      c2s_no_context_takeover = False
      s2c_max_window_bits = 0
      s2c_no_context_takeover = False

      for p in params:

         if len(params[p]) > 1:
            raise Exception("multiple occurence of extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

         val = params[p][0]

         if p == 'c2s_max_window_bits':
            if val not in ['8', '9', '10', '11', '12', '13', '14', '15']:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               c2s_max_window_bits = int(val)

         elif p == 'c2s_no_context_takeover':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               c2s_no_context_takeover = True

         elif p == 's2c_max_window_bits':
            if val not in ['8', '9', '10', '11', '12', '13', '14', '15']:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               s2c_max_window_bits = int(val)

         elif p == 's2c_no_context_takeover':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               s2c_no_context_takeover = True

         else:
            raise Exception("illegal extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

      response = Klass(c2s_max_window_bits,
                       c2s_no_context_takeover,
                       s2c_max_window_bits,
                       s2c_no_context_takeover)
      return response


   def __init__(self,
                c2s_max_window_bits,
                c2s_no_context_takeover,
                s2c_max_window_bits,
                s2c_no_context_takeover):
      self.c2s_max_window_bits = c2s_max_window_bits
      self.c2s_no_context_takeover = c2s_no_context_takeover
      self.s2c_max_window_bits = s2c_max_window_bits
      self.s2c_no_context_takeover = s2c_no_context_takeover



class PerMessageDeflateAccept(PerMessageCompressAccept, PerMessageDeflateMixin):
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



class PerMessageDeflate(PerMessageCompress, PerMessageDeflateMixin):
   """
   Negotiated parameters for permessage-deflate.
   """

   @classmethod
   def createFromResponse(Klass, isServer, response):
      pmce = Klass(isServer,
                   response.s2c_no_context_takeover,
                   response.c2s_no_context_takeover,
                   response.s2c_max_window_bits,
                   response.c2s_max_window_bits)
      return pmce


   def __init__(self,
                isServer,
                s2c_no_context_takeover,
                c2s_no_context_takeover,
                s2c_max_window_bits,
                c2s_max_window_bits):

      self._isServer = isServer
      self._compressor = None
      self._decompressor = None

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


   def startCompressMessage(self):
      if self._isServer:
         if self._compressor is None or self.s2c_no_context_takeover:
            self._compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -self.s2c_max_window_bits)
      else:
         if self._compressor is None or self.c2s_no_context_takeover:
            self._compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -self.c2s_max_window_bits)


   def compressMessageData(self, data):
      return self._compressor.compress(data)


   def endCompressMessage(self):
      data = self._compressor.flush(zlib.Z_SYNC_FLUSH)
      return data[:-4]


   def startDecompressMessage(self):
      if self._isServer:
         if self._decompressor is None or self.c2s_no_context_takeover:
            self._decompressor = zlib.decompressobj(-self.c2s_max_window_bits)
      else:
         if self._decompressor is None or self.s2c_no_context_takeover:
            self._decompressor = zlib.decompressobj(-self.s2c_max_window_bits)


   def decompressMessageData(self, data):
      return self._decompressor.decompress(data)


   def endDecompressMessage(self):
      ## Eat stripped LEN and NLEN field of a non-compressed block added
      ## for Z_SYNC_FLUSH.
      ##
      self._decompressor.decompress('\x00\x00\xff\xff')




class PerMessageBzip2Mixin:

   EXTENSION_NAME = "permessage-bzip2"



class PerMessageBzip2Offer(PerMessageCompressOffer, PerMessageBzip2Mixin):
   """
   Set of parameters for permessage-bzip2 offered by client.
   """

   @classmethod
   def parse(Klass, params):
      """
      Parses a WebSocket extension offer for permessage-deflate provided by a client to a server.
      """
      ## extension parameter defaults
      ##
      acceptCompressLevel = False
      requestCompressLevel = 0

      ##
      ## verify/parse c2s parameters of permessage-bzip2 extension
      ##
      for p in params:

         if len(params[p]) > 1:
            raise Exception("multiple occurence of extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

         val = params[p][0]

         if p == 'c2s_compress_level':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               acceptCompressLevel = True

         elif p == 's2c_compress_level':
            if val not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               requestCompressLevel = int(val)

         else:
            raise Exception("illegal extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

      offer = Klass(acceptCompressLevel, requestCompressLevel)
      return offer


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



class PerMessageBzip2Response(PerMessageCompressResponse, PerMessageBzip2Mixin):
   """
   Set of parameters for permessage-bzip2 responded by server.
   """

   @classmethod
   def parse(Klass, params):
      """
      Parses a WebSocket extension response for permessage-bzip2 provided by a server to a client.
      """
      c2s_compress_level = 0
      s2c_compress_level = 0

      for p in params:

         if len(params[p]) > 1:
            raise Exception("multiple occurence of extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

         val = params[p][0]

         if p == 'c2s_compress_level':
            if val not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               c2s_compress_level = int(val)

         elif p == 's2c_compress_level':
            if val not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               s2c_compress_level = int(val)

         else:
            raise Exception("illegal extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

      response = Klass(c2s_compress_level, s2c_compress_level)
      return response


   def __init__(self,
                c2s_compress_level,
                s2c_compress_level):
      self.c2s_compress_level = c2s_compress_level
      self.s2c_compress_level = s2c_compress_level



class PerMessageBzip2Accept(PerMessageCompressAccept, PerMessageBzip2Mixin):
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



class PerMessageBzip2(PerMessageCompress, PerMessageBzip2Mixin):
   """
   Negotiated parameters for permessage-bzip2.
   """

   @classmethod
   def createFromResponse(Klass, isServer, response):
      pmce = Klass(isServer,
                   response.s2c_compress_level,
                   response.c2s_compress_level)
      return pmce


   def __init__(self,
                isServer,
                s2c_compress_level,
                c2s_compress_level):

      self._isServer = isServer
      self._compressor = None
      self._decompressor = None

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


   def startCompressMessage(self):
      if self._isServer:
         if self._compressor is None:
            self._compressor = bz2.BZ2Compressor(self.s2c_compress_level)
      else:
         if self._compressor is None:
            self._compressor = bz2.BZ2Compressor(self.c2s_compress_level)


   def compressMessageData(self, data):
      return self._compressor.compress(data)


   def endCompressMessage(self):
      data = self._compressor.flush()
      self._compressor = None
      return data


   def startDecompressMessage(self):
      if self._decompressor is None:
         self._decompressor = bz2.BZ2Decompressor()


   def decompressMessageData(self, data):
      return self._decompressor.decompress(data)


   def endDecompressMessage(self):
      self._decompressor = None


# snappy.StreamCompressor
# .add_chunk(data)
# snappy.StreamDecompressor
# .decompress(data)


PERMESSAGE_COMPRESSION_EXTENSION = {

   PerMessageDeflateMixin.EXTENSION_NAME: {
      'Response': PerMessageDeflateResponse,
      'PMCE': PerMessageDeflate},

   PerMessageBzip2Mixin.EXTENSION_NAME: {
      'Response': PerMessageBzip2Response,
      'PMCE': PerMessageBzip2}
}
