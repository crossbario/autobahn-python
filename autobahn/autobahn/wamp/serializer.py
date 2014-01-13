###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
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

from __future__ import absolute_import

__all__ = ['WampSerializer',
           'JsonSerializer',
           'WampJsonSerializer']

from zope.interface import implementer

from autobahn.wamp.interfaces import ISerializer
from autobahn.wamp.exception import ProtocolError
from autobahn.wamp import message


class WampSerializer:
   """
   WAMP serializer is the core glue between parsed WAMP message objects and the
   bytes on wire (the transport).
   """

   MESSAGE_TYPE_MAP = {
      message.Hello.MESSAGE_TYPE:           message.Hello,
      message.Goodbye.MESSAGE_TYPE:         message.Goodbye,
      message.Heartbeat.MESSAGE_TYPE:       message.Heartbeat,
      message.Error.MESSAGE_TYPE:           message.Error,
      message.Publish.MESSAGE_TYPE:         message.Publish,
      message.Published.MESSAGE_TYPE:       message.Published,
      message.Subscribe.MESSAGE_TYPE:       message.Subscribe,
      message.Subscribed.MESSAGE_TYPE:      message.Subscribed,
      message.Unsubscribe.MESSAGE_TYPE:     message.Unsubscribe,
      message.Unsubscribed.MESSAGE_TYPE:    message.Unsubscribed,
      message.Event.MESSAGE_TYPE:           message.Event,
      message.Call.MESSAGE_TYPE:            message.Call,
      message.Cancel.MESSAGE_TYPE:          message.Cancel,
      message.Result.MESSAGE_TYPE:          message.Result,
      message.Register.MESSAGE_TYPE:        message.Register,
      message.Registered.MESSAGE_TYPE:      message.Registered,
      message.Unregister.MESSAGE_TYPE:      message.Unregister,
      message.Unregistered.MESSAGE_TYPE:    message.Unregistered,
      message.Invocation.MESSAGE_TYPE:      message.Invocation,
      message.Interrupt.MESSAGE_TYPE:       message.Interrupt,
      message.Yield.MESSAGE_TYPE:           message.Yield,
   }


   def __init__(self, serializer):
      """
      Constructor.

      :param serializer: The wire serializer to use for WAMP wire processing.
      :type serializer: An object that implements :class:`autobahn.interfaces.ISerializer`.
      """
      self._serializer = serializer


   def serialize(self, wampMessage):
      """
      Serializes a WAMP message to bytes to be sent to a transport.

      :param wampMessage: An instance of a subclass of :class:`autobahn.wamp2message.WampMessage`.
      :type wampMessage: obj
      :returns str -- A byte string.
      """
      return wampMessage.serialize(self._serializer), self._serializer.isBinary


   def unserialize(self, bytes, isBinary):
      """
      Unserializes bytes from a transport and parses a WAMP message.

      :param bytes: Byte string from wire.
      :type bytes: str or bytes
      :returns obj -- An instance of a subclass of :class:`autobahn.wamp2message.WampMessage`.
      """
      if isBinary != self._serializer.isBinary:
         raise ProtocolError("invalid serialization of WAMP message [binary = %s, but expected %s]" % (isBinary, self._serializer.isBinary))

      try:
         raw_msg = self._serializer.unserialize(bytes)
      except Exception as e:
         raise ProtocolError("invalid serialization of WAMP message [%s]" % e)

      if type(raw_msg) != list:
         raise ProtocolError("invalid type %s for WAMP message" % type(raw_msg))

      if len(raw_msg) == 0:
         raise ProtocolError("missing message type in WAMP message")

      message_type = raw_msg[0]

      if type(message_type) != int:
         raise ProtocolError("invalid type %d for WAMP message type" % type(message_type))

      Klass = self.MESSAGE_TYPE_MAP.get(message_type)

      if Klass is None:
         raise ProtocolError("invalid WAMP message type %d" % message_type)

      msg = Klass.parse(raw_msg)

      return msg



import json

@implementer(ISerializer)
class JsonSerializer:

   isBinary = False

   def serialize(self, obj):
      return json.dumps(obj, separators = (',',':'))


   def unserialize(self, bytes):
      return json.loads(bytes)



class WampJsonSerializer(WampSerializer):

   SERIALIZER_ID = "json"

   def __init__(self):
      WampSerializer.__init__(self, JsonSerializer())



try:
   import msgpack
except:
   pass
else:
   @implementer(ISerializer)
   class MsgPackSerializer:

      isBinary = True

      def serialize(self, obj):
         return msgpack.packb(obj, use_bin_type = True)


      def unserialize(self, bytes):
         return msgpack.unpackb(bytes, encoding = 'utf-8')

   __all__.append('MsgPackSerializer')


   class WampMsgPackSerializer(WampSerializer):

      SERIALIZER_ID = "msgpack"

      def __init__(self):
         WampSerializer.__init__(self, MsgPackSerializer())

   __all__.append('WampMsgPackSerializer')
