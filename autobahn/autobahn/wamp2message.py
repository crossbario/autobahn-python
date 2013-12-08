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


from zope.interface import implementer
import json

from interfaces import ISerializer


import urlparse, urllib


@implementer(ISerializer)
class JsonDefaultSerializer:

   def serialize(self, obj):
      return json.dumps(obj)


   def unserialize(self, bytes):
      return json.loads(bytes)



class WampException(Exception):
   pass

class WampProtocolError(WampException):
   pass



def parse_wamp_uri(bytes):
   try:
      uri = urllib.unquote(bytes).decode('utf8')
      parsed = urlparse.urlparse(uri)
   except:
      return None

   if parsed.scheme not in ["http", "https"]:
      return None

   if parsed.port is not None:
      return None

   if parsed.query is not None and parsed.query != "":
      return None

   return uri


class WampMessage:
   """
   WAMP message base class.
   """
   pass


class WampMessageSubscribe(WampMessage):
   """
   A WAMP Subscribe message.
   """

   MESSAGE_TYPE = 64 + 0

   MATCH_EXACT = 1
   MATCH_PREFIX = 2
   MATCH_WILDCARD = 3

   MATCH_DESC = {MATCH_EXACT: 'exact', MATCH_PREFIX: 'prefix', MATCH_WILDCARD: 'wildcard'}


   def __init__(self, topic, match = MATCH_EXACT):
      self.topic = topic
      self.match = match


   @classmethod
   def parse(Klass, wmsg):
      ## this should already be verified by WampSerializer.unserialize
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageSubscribe.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise WampProtocolError("invalid message length %d for WAMP Subscribe message" % len(wmsg))

      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for topic in WAMP Subscribe message" % type(wmsg[1]))

      topic = parse_wamp_uri(wmsg[1])
      if topic is None:
         raise WampProtocolError("invalid URI '%s' for topic in WAMP Subscribe message" % wmsg[1])

      match = WampMessageSubscribe.MATCH_EXACT

      if len(wmsg) == 3:
         options = wmsg[2]

         if type(options) != dict:
            raise WampProtocolError("invalid type %s for options in WAMP Subscribe message" % type(options))

         for k in options.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in options in WAMP Subscribe message" % type(k))

         if options.has_key('match'):

            option_match = options['match']
            if type(option_match) != int:
               raise WampProtocolError("invalid type %s for 'match' option in WAMP Subscribe message" % type(option_match))

            if option_match not in [WampMessageSubscribe.MATCH_EXACT, WampMessageSubscribe.MATCH_PREFIX, WampMessageSubscribe.MATCH_WILDCARD]:
               raise WampProtocolError("invalid value %d for 'match' option in WAMP Subscribe message" % option_match)

            match = option_match

      obj = Klass(topic, match)

      return obj

   
   def serialize(self, serializer):
      if self.match != WampMessageSubscribe.MATCH_EXACT:
         options = {'match': self.match}
         return serializer.serialize([self.MESSAGE_TYPE, self.topic, options])
      else:
         return serializer.serialize([self.MESSAGE_TYPE, self.topic])


   def __str__(self):
      return "WAMP Subscribe Message (topic = '%s', match = %s)" % (self.topic, WampMessageSubscribe.MATCH_DESC.get(self.match))



class WampMessageUnsubscribe(WampMessage):
   """
   A WAMP Unsubscribe message.
   """

   MESSAGE_TYPE = 64 + 1


   def __init__(self, topic, match = WampMessageSubscribe.MATCH_EXACT):
      self.topic = topic
      self.match = match


   @classmethod
   def parse(Klass, wmsg):
      ## this should already be verified by WampSerializer.unserialize
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageUnsubscribe.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise WampProtocolError("invalid message length %d for WAMP Unsubscribe message" % len(wmsg))

      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for topic in WAMP Unsubscribe message" % type(wmsg[1]))

      topic = parse_wamp_uri(wmsg[1])
      if topic is None:
         raise WampProtocolError("invalid URI '%s' for topic in WAMP Unsubscribe message" % wmsg[1])

      match = WampMessageSubscribe.MATCH_EXACT

      if len(wmsg) == 3:
         options = wmsg[2]

         if type(options) != dict:
            raise WampProtocolError("invalid type %s for options in WAMP Unsubscribe message" % type(options))

         for k in options.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in options in WAMP Unsubscribe message" % type(k))

         if options.has_key('match'):

            option_match = options['match']
            if type(option_match) != int:
               raise WampProtocolError("invalid type %s for 'match' option in WAMP Unsubscribe message" % type(option_match))

            if option_match not in [WampMessageSubscribe.MATCH_EXACT, WampMessageSubscribe.MATCH_PREFIX, WampMessageSubscribe.MATCH_WILDCARD]:
               raise WampProtocolError("invalid value %d for 'match' option in WAMP Unsubscribe message" % option_match)

            match = option_match

      obj = Klass(topic, match)

      return obj

   
   def serialize(self, serializer):
      if self.match != WampMessageSubscribe.MATCH_EXACT:
         options = {'match': self.match}
         return serializer.serialize([self.MESSAGE_TYPE, self.topic, options])
      else:
         return serializer.serialize([self.MESSAGE_TYPE, self.topic])


   def __str__(self):
      return "WAMP Unsubscribe Message (topic = '%s', match = %s)" % (self.topic, WampMessageSubscribe.MATCH_DESC.get(self.match))



class WampMessagePublish(WampMessage):
   """
   A WAMP Publish message.
   """

   MESSAGE_TYPE = 64 + 2


   def __init__(self, topic, event, excludeMe = None, exclude = None, eligible = None, identifyMe = None):
      self.topic = topic
      self.event = event
      self.excludeMe = excludeMe
      self.exclude = exclude
      self.eligible = eligible
      self.identifyMe = identifyMe


   @classmethod
   def parse(Klass, wmsg):
      ## this should already be verified by WampSerializer.unserialize
      assert(len(wmsg) > 0 and wmsg[0] == WampMessagePublish.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4):
         raise WampProtocolError("invalid message length %d for WAMP Publish message" % len(wmsg))

      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for topic in WAMP Publish message" % type(wmsg[1]))

      topic = parse_wamp_uri(wmsg[1])
      if topic is None:
         raise WampProtocolError("invalid URI '%s' for topic in WAMP Publish message" % wmsg[1])

      event = wmsg[2]

      excludeMe = None
      exclude = None
      eligible = None
      identifyMe = None

      if len(wmsg) == 4:
         options = wmsg[3]

         if type(options) != dict:
            raise WampProtocolError("invalid type %s for options in WAMP Publish message" % type(options))

         for k in options.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in options in WAMP Publish message" % type(k))

         if options.has_key('excludeme'):

            option_excludeMe = options['excludeme']
            if type(option_excludeMe) != bool:
               raise WampProtocolError("invalid type %s for 'excludeme' option in WAMP Publish message" % type(option_excludeMe))

            excludeMe = option_excludeMe

         if options.has_key('exclude'):

            option_exclude = options['exclude']
            if type(option_exclude) != list:
               raise WampProtocolError("invalid type %s for 'exclude' option in WAMP Publish message" % type(option_exclude))

            for sessionId in option_exclude:
               if type(sessionId) not in (str, unicode):
                  raise WampProtocolError("invalid type %s for value in 'exclude' option in WAMP Publish message" % type(sessionId))

            exclude = option_exclude

         if options.has_key('eligible'):

            option_eligible = options['eligible']
            if type(option_eligible) != list:
               raise WampProtocolError("invalid type %s for 'eligible' option in WAMP Publish message" % type(option_eligible))

            for sessionId in option_eligible:
               if type(sessionId) not in (str, unicode):
                  raise WampProtocolError("invalid type %s for value in 'eligible' option in WAMP Publish message" % type(sessionId))

            eligible = option_eligible

         if options.has_key('identifyme'):

            option_identifyMe = options['identifyme']
            if type(option_identifyMe) != bool:
               raise WampProtocolError("invalid type %s for 'identifyme' option in WAMP Publish message" % type(option_identifyMe))

            identifyMe = option_identifyMe

      obj = Klass(topic, event, excludeMe, exclude, eligible, identifyMe)

      return obj

   
   def serialize(self, serializer):
      options = {}

      if self.excludeMe is not None:
         options['excludeme'] = excludeMe
      if self.exclude is not None:
         options['exclude'] = exclude
      if self.eligible is not None:
         options['eligible'] = eligible
      if self.identifyMe is not None:
         options['identifyme'] = identifyMe

      if len(options):
         return serializer.serialize([WampMessagePublish.MESSAGE_TYPE, self.topic, self.event, options])
      else:
         return serializer.serialize([WampMessagePublish.MESSAGE_TYPE, self.topic, self.event])


   def __str__(self):
      return "WAMP Publish Message (topic = '%s', event = %s, excludeMe = %s, exclude = %s, eligible = %s, identifyMe = %s)" % (self.topic, self.event, self.excludeMe, self.exclude, self.eligible, self.identifyMe)



class WampMessageEvent(WampMessage):
   """
   A WAMP Event message.
   """

   MESSAGE_TYPE = 64 + 3


   def __init__(self, topic, event = None, publisher = None):
      self.topic = topic
      self.event = event
      self.publisher = publisher


   @classmethod
   def parse(Klass, wmsg):
      ## this should already be verified by WampSerializer.unserialize
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageEvent.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3, 4):
         raise WampProtocolError("invalid message length %d for WAMP Publish message" % len(wmsg))

      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for topic in WAMP Publish message" % type(wmsg[1]))

      topic = parse_wamp_uri(wmsg[1])
      if topic is None:
         raise WampProtocolError("invalid URI '%s' for topic in WAMP Publish message" % wmsg[1])

      event = None
      if len(wmsg) > 2:
         event = wmsg[2]

      publisher = None

      if len(wmsg) == 4:
         options = wmsg[3]

         if type(options) != dict:
            raise WampProtocolError("invalid type %s for options in WAMP Publish message" % type(options))

         for k in options.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in options in WAMP Publish message" % type(k))

         if options.has_key('publisher'):

            option_publisher = options['publisher']
            if type(option_publisher) not in (str, unicode):
               raise WampProtocolError("invalid type %s for 'publisher' option in WAMP Publish message" % type(option_publisher))

            publisher = option_publisher

      obj = Klass(topic, event, publisher)

      return obj

   
   def serialize(self, serializer):
      options = {}

      if self.publisher is not None:
         options['publisher'] = publisher

      if len(options):
         return serializer.serialize([WampMessagePublish.MESSAGE_TYPE, self.topic, self.event, options])
      else:
         if self.event is not None:
            return serializer.serialize([WampMessagePublish.MESSAGE_TYPE, self.topic, self.event])
         else:
            return serializer.serialize([WampMessagePublish.MESSAGE_TYPE, self.topic])


   def __str__(self):
      return "WAMP Publish Message (topic = '%s', event = %s, publisher = %s)" % (self.topic, self.event, self.publisher)



class WampSerializer:
   """
   WAMP serializer is the core glue between parsed WAMP message objects and the
   bytes on wire (the transport).
   """

   MESSAGE_TYPE_MAP = {
      WampMessageSubscribe.MESSAGE_TYPE: WampMessageSubscribe,
      WampMessageUnsubscribe.MESSAGE_TYPE: WampMessageUnsubscribe,
      WampMessagePublish.MESSAGE_TYPE: WampMessagePublish,
      WampMessageEvent.MESSAGE_TYPE: WampMessageEvent,
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
      return wampMessage.serialize(self._serializer)


   def unserialize(self, bytes):
      """
      Unserializes bytes from a transport and parses a WAMP message.

      :param bytes: Byte string from wire.
      :type bytes: str or bytes
      :returns obj -- An instance of a subclass of :class:`autobahn.wamp2message.WampMessage`.
      """
      raw_msg = self._serializer.unserialize(bytes)

      if type(raw_msg) != list:
         raise WampProtocolError("invalid type %s for WAMP message" % type(raw_msg))

      if len(raw_msg) == 0:
         raise WampProtocolError("missing message type in WAMP message")

      message_type = raw_msg[0]

      if type(message_type) != int:
         raise WampProtocolError("invalid type %d for WAMP message type" % type(message_type))

      Klass = self.MESSAGE_TYPE_MAP.get(message_type)

      if Klass is None:
         raise WampProtocolError("invalid WAMP message type %d" % message_type)

      msg = Klass.parse(raw_msg)

      return msg



if __name__ == '__main__':

   serializer = JsonDefaultSerializer()

   wampSerializer = WampSerializer(serializer)

   wampMsg = WampMessageSubscribe("http://myapp.com/topic1", match = WampMessageSubscribe.MATCH_PREFIX)
   wampMsg = WampMessageUnsubscribe("http://myapp.com/topic1", match = WampMessageSubscribe.MATCH_PREFIX)
   wampMsg = WampMessagePublish("http://myapp.com/topic1", "Hello, world!")

   bytes = wampSerializer.serialize(wampMsg)

   print bytes

   wampMsg2 = wampSerializer.unserialize(bytes)

   print wampMsg2.__class__
   print wampMsg2
