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

__all__ = ["PerMessageSnappyMixin",
           "PerMessageSnappyOffer",
           "PerMessageSnappyResponse",
           "PerMessageSnappyAccept",
           "PerMessageSnappy"]


import snappy

from compress_base import PerMessageCompressOffer, \
                          PerMessageCompressResponse, \
                          PerMessageCompressAccept, \
                          PerMessageCompress


class PerMessageSnappyMixin:

   EXTENSION_NAME = "permessage-snappy"



class PerMessageSnappyOffer(PerMessageCompressOffer, PerMessageSnappyMixin):
   """
   Set of parameters for permessage-snappy offered by client.
   """

   @classmethod
   def parse(Klass, params):
      """
      Parses a WebSocket extension offer for permessage-deflate provided by a client to a server.
      """
      ## extension parameter defaults
      ##
      acceptNoContextTakeover = False
      requestNoContextTakeover = False

      ##
      ## verify/parse c2s parameters of permessage-snappy extension
      ##
      for p in params:

         if len(params[p]) > 1:
            raise Exception("multiple occurence of extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

         val = params[p][0]

         if p == 'c2s_no_context_takeover':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               acceptNoContextTakeover = True

         elif p == 's2c_no_context_takeover':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               requestNoContextTakeover = True

         else:
            raise Exception("illegal extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

      offer = Klass(acceptNoContextTakeover, requestNoContextTakeover)
      return offer


   def __init__(self,
                acceptNoContextTakeover = True,
                requestNoContextTakeover = False):
      """
      Constructor.

      :param acceptNoContextTakeover: Iff true, client accepts "no context takeover" feature.
      :type acceptNoContextTakeover: bool
      :param requestNoContextTakeover: Iff true, client request "no context takeover" feature.
      :type requestNoContextTakeover: bool
      """
      self.acceptNoContextTakeover = acceptNoContextTakeover
      self.requestNoContextTakeover = requestNoContextTakeover

      e = self.EXTENSION_NAME
      if self.acceptNoContextTakeover:
         e += "; c2s_no_context_takeover"
      if self.requestNoContextTakeover:
         e += "; s2c_no_context_takeover"
      self._pmceString = e


   def getExtensionString(self):
      """
      Returns the WebSocket extension configuration string.
      """
      return self._pmceString


   def __json__(self):
      return {'acceptNoContextTakeover': self.acceptNoContextTakeover,
              'requestNoContextTakeover': self.requestNoContextTakeover}


   def __repr__(self):
      return "PerMessageSnappyOffer(acceptNoContextTakeover = %s, requestNoContextTakeover = %s)" % (self.acceptNoContextTakeover, self.requestNoContextTakeover)



class PerMessageSnappyResponse(PerMessageCompressResponse, PerMessageSnappyMixin):
   """
   Set of parameters for permessage-snappy responded by server.
   """

   @classmethod
   def parse(Klass, params):
      """
      Parses a WebSocket extension response for permessage-snappy provided by a server to a client.
      """
      c2s_no_context_takeover = False
      s2c_no_context_takeover = False

      for p in params:

         if len(params[p]) > 1:
            raise Exception("multiple occurence of extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

         val = params[p][0]

         if p == 'c2s_no_context_takeover':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               c2s_no_context_takeover = True

         elif p == 's2c_no_context_takeover':
            if val != True:
               raise Exception("illegal extension parameter value '%s' for parameter '%s' of extension '%s'" % (val, p, Klass.EXTENSION_NAME))
            else:
               s2c_no_context_takeover = True

         else:
            raise Exception("illegal extension parameter '%s' for extension '%s'" % (p, Klass.EXTENSION_NAME))

      response = Klass(c2s_no_context_takeover,
                       s2c_no_context_takeover)
      return response


   def __init__(self,
                c2s_no_context_takeover,
                s2c_no_context_takeover):
      self.c2s_no_context_takeover = c2s_no_context_takeover
      self.s2c_no_context_takeover = s2c_no_context_takeover



class PerMessageSnappyAccept(PerMessageCompressAccept, PerMessageSnappyMixin):
   """
   Set of parameters with which to accept an permessage-snappy offer
   from a client by a server.
   """

   def __init__(self,
                offer,
                requestNoContextTakeover = False):
      self.offer = offer
      self.requestNoContextTakeover = requestNoContextTakeover


   def __json__(self):
      return {'requestNoContextTakeover': self.requestNoContextTakeover}




class PerMessageSnappy(PerMessageCompress, PerMessageSnappyMixin):
   """
   Negotiated parameters for permessage-snappy.
   """

   @classmethod
   def createFromResponse(Klass, isServer, response):
      pmce = Klass(isServer,
                   response.s2c_no_context_takeover,
                   response.c2s_no_context_takeover)
      return pmce


   @classmethod
   def createFromAccept(Klass, isServer, accept):
      pmce = Klass(isServer,
                   accept.offer.requestNoContextTakeover,
                   accept.requestNoContextTakeover)
      return pmce


   def __init__(self,
                isServer,
                s2c_no_context_takeover,
                c2s_no_context_takeover):

      self._isServer = isServer
      self._compressor = None
      self._decompressor = None

      self.s2c_no_context_takeover = s2c_no_context_takeover
      self.c2s_no_context_takeover = c2s_no_context_takeover

      s = self.EXTENSION_NAME
      if s2c_no_context_takeover:
         s += "; s2c_no_context_takeover"
      if c2s_no_context_takeover:
         s += "; c2s_no_context_takeover"
      self._pmceString = s


   def getExtensionString(self):
      return self._pmceString


   def startCompressMessage(self):
      if self._isServer:
         if self._compressor is None or self.s2c_no_context_takeover:
            self._compressor = snappy.StreamCompressor()
      else:
         if self._compressor is None or self.c2s_no_context_takeover:
            self._compressor = snappy.StreamCompressor()


   def compressMessageData(self, data):
      return self._compressor.add_chunk(data)


   def endCompressMessage(self):
      return ""


   def startDecompressMessage(self):
      if self._isServer:
         if self._decompressor is None or self.c2s_no_context_takeover:
            self._decompressor = snappy.StreamDecompressor()
      else:
         if self._decompressor is None or self.s2c_no_context_takeover:
            self._decompressor = snappy.StreamDecompressor()


   def decompressMessageData(self, data):
      return self._decompressor.decompress(data)


   def endDecompressMessage(self):
      pass
