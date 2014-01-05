###############################################################################
##
##  Copyright (C) 2013-2014 Tavendo GmbH
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


from interfaces import ISerializer


import urlparse, urllib


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



def parse_wamp_sessionid(string):
   ## FIXME: verify/parse WAMP session ID
   return string



def parse_wamp_callid(string):
   ## FIXME: verify/parse WAMP call ID
   return string



class WampMessage:
   """
   WAMP message base class.
   """
   def __init__(self):
      self.resetSerialization()

   def resetSerialization(self):
      ## serialization cache: mapping from ISerializer instances
      ## to serialized bytes
      ##
      self._serialized = {}

   def serialize(self, serializer):
      if not self._serialized.has_key(serializer):
         #print "WampMessage.serialize [new]", serializer
         self._serialized[serializer] = serializer.serialize(self.marshal())
      else:
         #print "WampMessage.serialize [cached]", serializer
         pass

      return self._serialized[serializer]

   def __eq__(self, other):
      return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

   def __ne__(self, other):
      return not self.__eq__(other)



class WampMessageError(WampMessage):
   """
   A WAMP Error message base class.
   """

   def __init__(self, requestid, error, message = None, value = None):
      """
      Message constructor.

      :param requestid: The WAMP request ID (callid, subscribeid, ..) of the original request (call, subscribe, ..) this error is for.
      :type requestid: str
      :param error: The WAMP or application error URI for the error that occured.
      :type error: str
      :param message: Human readable error message.
      :type message: str
      :param value: Arbitrary error value to transport error detail data for programatic consumption (must be serializable using the serializer in use).
      :type value: any
      """
      WampMessage.__init__(self)
      self.requestid = requestid
      self.error = error
      self.message = message
      self.value = value


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == Klass.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4):
         raise WampProtocolError("invalid message length %d for WAMP Error message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'requestid' in WAMP Error message" % type(wmsg[1]))

      requestid = parse_wamp_callid(wmsg[1])
      if requestid is None:
         raise WampProtocolError("invalid value '%s' for 'requestid' in WAMP Error message" % wmsg[1])

      ## error
      ##
      if type(wmsg[2]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'error' in WAMP Error message" % type(wmsg[2]))

      error = parse_wamp_uri(wmsg[2])
      if error is None:
         raise WampProtocolError("invalid value '%s' for 'error' in WAMP Error message" % wmsg[2])

      ## details
      ##
      message = None
      value = None

      if len(wmsg) == 4:
         details = wmsg[3]

         if type(details) != dict:
            raise WampProtocolError("invalid type %s for 'details' in WAMP Error message" % type(details))

         for k in details.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key '%s' in 'details' in WAMP Error message" % (k, type(k)))

         ## error message (should be human readable)
         ##
         if details.has_key('message'):

            option_message = options['message']
            if type(option_message) not in (str, unicode):
               raise WampProtocolError("invalid type %s for 'message' option in WAMP Error message" % type(option_message))

            message = option_message

         ## arbitrary application error value
         ##
         value = details['value']

      obj = Klass(requestid, error, message = message, value = value)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      details = {}

      if self.message is not None:
         details['message'] = self.message

      if self.value is not None:
         details['value'] = self.value

      if len(details):
         return [self.MESSAGE_TYPE, self.requestid, self.error, details]
      else:
         return [self.MESSAGE_TYPE, self.requestid, self.error]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Error Message (requestid = '%s', error = '%s', message = '%s', value = %s)" % (self.requestid, self.error, self.message, self.value)



class WampMessageHello(WampMessage):
   """
   A WAMP Hello message.
   """

   MESSAGE_TYPE = 1
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, sessionid):
      """
      Message constructor.

      :param sessionid: The WAMP session ID the other peer is assigned.
      :type sessionid: str
      """
      WampMessage.__init__(self)
      self.sessionid = sessionid


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageHello.MESSAGE_TYPE)

      if len(wmsg) != 2:
         raise WampProtocolError("invalid message length %d for WAMP Hello message" % len(wmsg))

      ## sessionid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'sessionid' in WAMP Hello message" % type(wmsg[1]))

      sessionid = parse_wamp_sessionid(wmsg[1])
      if sessionid is None:
         raise WampProtocolError("invalid value '%s' for 'sessionid' in WAMP Hello message" % wmsg[1])

      obj = Klass(sessionid)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [WampMessageHello.MESSAGE_TYPE, self.sessionid]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Hello Message (sessionid = '%s')" % (self.sessionid)



class WampMessageRoleChange(WampMessage):
   """
   A WAMP Role-Change message.
   """

   MESSAGE_TYPE = 23
   """
   The WAMP message code for this type of message.
   """

   ROLE_CHANGE_OP_ADD = 1
   ROLE_CHANGE_OP_REMOVE = 2

   ROLE_CHANGE_OP_DESC = {
      ROLE_CHANGE_OP_ADD: 'add',
      ROLE_CHANGE_OP_REMOVE: 'remove'
   }

   ROLE_CHANGE_ROLE_BROKER = 'broker'
   ROLE_CHANGE_ROLE_DEALER = 'dealer'


   def __init__(self, op, role):
      """
      Message constructor.

      :param op: Role operation (add or remove role).
      :type op: int
      :param role: Role to be added or removed.
      :type role: str
      """
      WampMessage.__init__(self)
      self.op = op
      self.role = role


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageRoleChange.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise WampProtocolError("invalid message length %d for WAMP Role-Change message" % len(wmsg))

      ## op
      ##
      op = wmsg[1]
      if type(op) != int:
         raise WampProtocolError("invalid type %s for 'op' in WAMP Role-Change message" % type(op))
      if op not in [WampMessageRoleChange.ROLE_CHANGE_OP_ADD, WampMessageRoleChange.ROLE_CHANGE_OP_REMOVE]:
         raise WampProtocolError("invalid value '%s' for 'op' in WAMP Role-Change message" % op)

      ## role
      ##
      role = wmsg[2]
      if type(role) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'role' in WAMP Role-Change message" % type(role))
      if role not in [WampMessageRoleChange.ROLE_CHANGE_ROLE_BROKER, WampMessageRoleChange.ROLE_CHANGE_ROLE_DEALER]:
         raise WampProtocolError("invalid value '%s' for 'role' in WAMP Role-Change message" % role)

      obj = Klass(op, role)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [WampMessageRoleChange.MESSAGE_TYPE, self.op, self.role]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Role-Change Message (op = '%s', role = '%s')" % (WampMessageRoleChange.ROLE_CHANGE_OP_DESC.get(self.op), self.role)



class WampMessageHeartbeat(WampMessage):
   """
   A WAMP Hearbeat message.
   """

   MESSAGE_TYPE = 2
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, incoming, outgoing):
      """
      Message constructor.

      :param incoming: Last incoming heartbeat processed from peer.
      :type incoming: int
      :param outgoing: Outgoing heartbeat.
      :type outgoing: int
      """
      WampMessage.__init__(self)
      self.incoming = incoming
      self.outgoing = outgoing


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageHeartbeat.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise WampProtocolError("invalid message length %d for WAMP Heartbeat message" % len(wmsg))

      ## incoming
      ##
      incoming = wmsg[1]

      if type(incoming) != int:
         raise WampProtocolError("invalid type %s for 'incoming' in WAMP Heartbeat message" % type(incoming))

      if incoming < 0: # must be non-negative
         raise WampProtocolError("invalid value %d for 'incoming' in WAMP Heartbeat message" % incoming)

      ## outgoing
      ##
      outgoing = wmsg[2]

      if type(outgoing) != int:
         raise WampProtocolError("invalid type %s for 'outgoing' in WAMP Heartbeat message" % type(outgoing))

      if outgoing <= 0: # must be positive
         raise WampProtocolError("invalid value %d for 'outgoing' in WAMP Heartbeat message" % outgoing)

      obj = Klass(incoming, outgoing)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [WampMessageHeartbeat.MESSAGE_TYPE, self.incoming, self.outgoing]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Hearbeat Message (incoming %d, outgoing = %d)" % (self.incoming, self.outgoing)



class WampMessageSubscribe(WampMessage):
   """
   A WAMP Subscribe message.
   """

   MESSAGE_TYPE = 3
   """
   The WAMP message code for this type of message.
   """

   MATCH_EXACT = 1
   MATCH_PREFIX = 2
   MATCH_WILDCARD = 3

   MATCH_DESC = {MATCH_EXACT: 'exact', MATCH_PREFIX: 'prefix', MATCH_WILDCARD: 'wildcard'}


   def __init__(self, subscribeid, topic, match = MATCH_EXACT):
      """
      Message constructor.

      :param topic: The WAMP or application URI of the PubSub topic to subscribe to.
      :type topic: str
      :param match: The topic matching method to be used for the subscription.
      :type match: int
      """
      WampMessage.__init__(self)
      self.subscribeid = subscribeid
      self.topic = topic
      self.match = match


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageSubscribe.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4):
         raise WampProtocolError("invalid message length %d for WAMP Subscribe message" % len(wmsg))

      ## subscribeid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'subscribeid' in WAMP Subscribe message" % type(wmsg[1]))

      subscribeid = parse_wamp_callid(wmsg[1])
      if subscribeid is None:
         raise WampProtocolError("invalid value '%s' for 'subscribeid' in WAMP Subscribe message" % wmsg[1])

      ## topic
      ##
      if type(wmsg[2]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for topic in WAMP Subscribe message" % type(wmsg[2]))

      topic = parse_wamp_uri(wmsg[2])
      if topic is None:
         raise WampProtocolError("invalid value '%s' for topic in WAMP Subscribe message" % wmsg[2])

      ## options
      ##
      match = WampMessageSubscribe.MATCH_EXACT

      if len(wmsg) == 4:
         options = wmsg[3]

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

      obj = Klass(subscribeid, topic, match)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      options = {}

      if self.match != WampMessageSubscribe.MATCH_EXACT:
         options['match'] = self.match

      if len(options):
         return [WampMessageSubscribe.MESSAGE_TYPE, self.subscribeid, self.topic, options]
      else:
         return [WampMessageSubscribe.MESSAGE_TYPE, self.subscribeid, self.topic]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Subscribe Message (subscribeid = '%s', topic = '%s', match = %s)" % (self.subscribeid, self.topic, WampMessageSubscribe.MATCH_DESC.get(self.match))



class WampMessageSubscription(WampMessage):
   """
   A WAMP Subscription message.
   """

   MESSAGE_TYPE = 103
   """
   The WAMP message code for this type of message.
   """

   def __init__(self, subscribeid, subscriptionid):
      """
      Message constructor.

      :param topic: The WAMP or application URI of the PubSub topic to subscribe to.
      :type topic: str
      :param match: The topic matching method to be used for the subscription.
      :type match: int
      """
      WampMessage.__init__(self)
      self.subscribeid = subscribeid
      self.subscriptionid = subscriptionid


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageSubscription.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise WampProtocolError("invalid message length %d for WAMP Subscribe message" % len(wmsg))

      ## subscribeid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'subscribeid' in WAMP Subscription message" % type(wmsg[1]))

      subscribeid = parse_wamp_callid(wmsg[1])
      if subscribeid is None:
         raise WampProtocolError("invalid value '%s' for 'subscribeid' in WAMP Subscription message" % wmsg[1])

      ## subscriptionid
      ##
      if type(wmsg[2]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'subscriptionid' in WAMP Subscription message" % type(wmsg[2]))

      subscriptionid = parse_wamp_callid(wmsg[2])
      if subscriptionid is None:
         raise WampProtocolError("invalid value '%s' for 'subscriptionid' in WAMP Subscription message" % wmsg[2])

      obj = Klass(subscribeid, subscriptionid)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [WampMessageSubscription.MESSAGE_TYPE, self.subscribeid, self.subscriptionid]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Subscription Message (subscribeid = '%s', subscriptionid = '%s')" % (self.subscribeid, self.subscriptionid)



class WampMessageSubscribeError(WampMessageError):
   """
   A WAMP Subscribe-Error message.
   """

   MESSAGE_TYPE = 104
   """
   The WAMP message code for this type of message.
   """



class WampMessageUnsubscribe(WampMessage):
   """
   A WAMP Unsubscribe message.
   """

   MESSAGE_TYPE = 4
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, topic, match = WampMessageSubscribe.MATCH_EXACT):
      """
      Message constructor.

      :param topic: The WAMP or application URI of the PubSub topic to unsubscribe from.
      :type topic: str
      :param match: The topic matching method effective for the subscription to unsubscribe from.
      :type match: int
      """
      WampMessage.__init__(self)
      self.topic = topic
      self.match = match


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageUnsubscribe.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise WampProtocolError("invalid message length %d for WAMP Unsubscribe message" % len(wmsg))

      ## topic
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for topic in WAMP Unsubscribe message" % type(wmsg[1]))

      topic = parse_wamp_uri(wmsg[1])
      if topic is None:
         raise WampProtocolError("invalid URI '%s' for topic in WAMP Unsubscribe message" % wmsg[1])

      ## options
      ##
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

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      options = {}

      if self.match != WampMessageSubscribe.MATCH_EXACT:
         options['match'] = self.match

      if len(options):
         return [WampMessageUnsubscribe.MESSAGE_TYPE, self.topic, options]
      else:
         return [WampMessageUnsubscribe.MESSAGE_TYPE, self.topic]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Unsubscribe Message (topic = '%s', match = %s)" % (self.topic, WampMessageSubscribe.MATCH_DESC.get(self.match))



class WampMessagePublish(WampMessage):
   """
   A WAMP Publish message.
   """

   MESSAGE_TYPE = 5
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, topic, event, excludeMe = None, exclude = None, eligible = None, discloseMe = None):
      """
      Message constructor.

      :param topic: The WAMP or application URI of the PubSub topic the event should be published to.
      :type topic: str
      :param event: Arbitrary application event payload (must be serializable using the serializer in use).
      :type event: any
      :param excludeMe: If True, exclude the publisher from receiving the event, even if he is subscribed (and eligible).
      :type excludeMe: bool
      :param exclude: List of WAMP session IDs to exclude from receiving this event.
      :type exclude: list
      :param eligible: List of WAMP session IDs eligible to receive this event.
      :type eligible: list
      :param discloseMe: If True, request to disclose the publisher of this event to subscribers.
      :type discloseMe: bool
      """
      WampMessage.__init__(self)
      self.topic = topic
      self.event = event
      self.excludeMe = excludeMe
      self.exclude = exclude
      self.eligible = eligible
      self.discloseMe = discloseMe


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessagePublish.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4):
         raise WampProtocolError("invalid message length %d for WAMP Publish message" % len(wmsg))

      ## topic
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for topic in WAMP Publish message" % type(wmsg[1]))

      topic = parse_wamp_uri(wmsg[1])
      if topic is None:
         raise WampProtocolError("invalid URI '%s' for topic in WAMP Publish message" % wmsg[1])

      ## event
      ##
      event = wmsg[2]

      ## options
      ##
      excludeMe = None
      exclude = None
      eligible = None
      discloseMe = None

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

         if options.has_key('discloseme'):

            option_discloseMe = options['discloseme']
            if type(option_discloseMe) != bool:
               raise WampProtocolError("invalid type %s for 'discloseme' option in WAMP Publish message" % type(option_identifyMe))

            discloseMe = option_discloseMe

      obj = Klass(topic, event, excludeMe, exclude, eligible, discloseMe)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      options = {}

      if self.excludeMe is not None:
         options['excludeme'] = self.excludeMe
      if self.exclude is not None:
         options['exclude'] = self.exclude
      if self.eligible is not None:
         options['eligible'] = self.eligible
      if self.discloseMe is not None:
         options['discloseme'] = self.discloseMe

      if len(options):
         return [WampMessagePublish.MESSAGE_TYPE, self.topic, self.event, options]
      else:
         return [WampMessagePublish.MESSAGE_TYPE, self.topic, self.event]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Publish Message (topic = '%s', event = %s, excludeMe = %s, exclude = %s, eligible = %s, discloseMe = %s)" % (self.topic, self.event, self.excludeMe, self.exclude, self.eligible, self.discloseMe)



class WampMessageEvent(WampMessage):
   """
   A WAMP Event message.
   """

   MESSAGE_TYPE = 6
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, subscriptionid, topic, event = None, publisher = None):
      """
      Message constructor.

      :param topic: The WAMP or application URI of the PubSub topic the event was published to.
      :type topic: str
      :param event: Arbitrary application event payload (must be serializable using the serializer in use).
      :type event: any
      :param publisher: If present, the WAMP session ID of the publisher of this event.
      :type publisher: str
      """
      WampMessage.__init__(self)
      self.subscriptionid = subscriptionid
      self.topic = topic
      self.event = event
      self.publisher = publisher


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageEvent.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4, 5):
         raise WampProtocolError("invalid message length %d for WAMP Event message" % len(wmsg))

      ## subscriptionid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'subscriptionid' in WAMP Event message" % type(wmsg[1]))

      subscriptionid = parse_wamp_callid(wmsg[1])
      if subscriptionid is None:
         raise WampProtocolError("invalid value '%s' for 'subscriptionid' in WAMP Event message" % wmsg[1])

      ## topic
      ##
      if type(wmsg[2]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for topic in WAMP Event message" % type(wmsg[2]))

      topic = parse_wamp_uri(wmsg[2])
      if topic is None:
         raise WampProtocolError("invalid URI '%s' for topic in WAMP Event message" % wmsg[2])

      ## event
      ##
      event = None
      if len(wmsg) > 3:
         event = wmsg[3]

      ## details
      ##
      publisher = None

      if len(wmsg) > 4:
         details = wmsg[4]

         if type(details) != dict:
            raise WampProtocolError("invalid type %s for 'details' in WAMP Event message" % type(details))

         for k in details.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in 'details' in WAMP Event message" % type(k))

         if details.has_key('publisher'):

            detail_publisher = details['publisher']
            if type(detail_publisher) not in (str, unicode):
               raise WampProtocolError("invalid type %s for 'publisher' detail in WAMP Event message" % type(detail_publisher))

            publisher = detail_publisher

      obj = Klass(subscriptionid, topic, event, publisher)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      details = {}

      if self.publisher is not None:
         details['publisher'] = self.publisher

      if len(details):
         return [WampMessageEvent.MESSAGE_TYPE, self.topic, self.event, details]
      else:
         if self.event is not None:
            return [WampMessageEvent.MESSAGE_TYPE, self.subscriptionid, self.topic, self.event]
         else:
            return [WampMessageEvent.MESSAGE_TYPE, self.subscriptionid, self.topic]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Publish Message (subscriptionid = '%s', topic = '%s', event = %s, publisher = %s)" % (self.subscriptionid, self.topic, self.event, self.publisher)



class WampMessageMetaEvent(WampMessage):
   """
   A WAMP Meta-Event message.
   """

   MESSAGE_TYPE = 7
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, topic, metatopic, metaevent = None):
      """
      Message constructor.

      :param topic: The WAMP or application URI of the PubSub topic the metaevent is published for.
      :type topic: str
      :param metatopic: The WAMP URI of the metatopic of the metaevent.
      :type metatopic: str
      :param metaevent: WAMP metaevent payload.
      :type metaevent: any
      """
      WampMessage.__init__(self)
      self.topic = topic
      self.metatopic = metatopic
      self.metaevent = metaevent


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageMetaEvent.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4):
         raise WampProtocolError("invalid message length %d for WAMP Meta-Event message" % len(wmsg))

      ## topic
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'topic' in WAMP Meta-Event message" % type(wmsg[1]))

      topic = parse_wamp_uri(wmsg[1])
      if topic is None:
         raise WampProtocolError("invalid URI '%s' for 'topic' in WAMP Meta-Event message" % wmsg[1])

      ## metatopic
      ##
      if type(wmsg[2]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'metatopic' in WAMP Meta-Event message" % type(wmsg[2]))

      metatopic = parse_wamp_uri(wmsg[2])
      if metatopic is None:
         raise WampProtocolError("invalid URI '%s' for 'metatopic' in WAMP Meta-Event message" % wmsg[2])

      ## metaevent
      ##
      metaevent = None
      if len(wmsg) == 4:
         metaevent = wmsg[3]

      obj = Klass(topic, metatopic, metaevent)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      if self.metaevent is not None:
         return [WampMessageMetaEvent.MESSAGE_TYPE, self.topic, self.metatopic, self.metaevent]
      else:
         return [WampMessageMetaEvent.MESSAGE_TYPE, self.topic, self.metatopic]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Meta-Event Message (topic = '%s', metatopic = '%s', metaevent = %s)" % (self.topic, self.metatopic, self.metaevent)



class WampMessageProvide(WampMessage):
   """
   A WAMP Provide message.
   """

   MESSAGE_TYPE = 8
   """
   The WAMP message code for this type of message.
   """

   def __init__(self, endpoint, pkeys = None):
      """
      Message constructor.

      :param endpoint: The WAMP or application URI of the RPC endpoint provided.
      :type endpoint: str
      :param pkeys: The endpoint can work for this list of application partition keys.
      :type pkeys: list
      """
      WampMessage.__init__(self)
      self.endpoint = endpoint
      self.pkeys = pkeys


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageProvide.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise WampProtocolError("invalid message length %d for WAMP Provide message" % len(wmsg))

      ## topic
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'endpoint' in WAMP Provide message" % type(wmsg[1]))

      endpoint = parse_wamp_uri(wmsg[1])
      if endpoint is None:
         raise WampProtocolError("invalid URI '%s' for 'endpoint' in WAMP Provide message" % wmsg[1])

      ## options
      ##
      pkeys = None

      if len(wmsg) == 3:
         options = wmsg[2]

         if type(options) != dict:
            raise WampProtocolError("invalid type %s for 'options' in WAMP Provide message" % type(options))

         for k in options.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in 'options' in WAMP Provide message" % type(k))

         if options.has_key('pkeys'):

            option_pkeys = options['pkeys']
            if type(option_pkeys) != list:
               raise WampProtocolError("invalid type %s for 'pkeys' option in WAMP Provide message" % type(option_pkeys))

            for pk in option_pkeys:
               if type(pk) not in (str, unicode):
                  raise WampProtocolError("invalid type for value '%s' in 'pkeys' option in WAMP Provide message" % type(pk))

            pkeys = option_pkeys

      obj = Klass(endpoint, pkeys)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      options = {}

      if self.pkeys is not None:
         options['pkeys'] = self.pkeys

      if len(options):
         return [WampMessageProvide.MESSAGE_TYPE, self.endpoint, options]
      else:
         return [WampMessageProvide.MESSAGE_TYPE, self.endpoint]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Provide Message (endpoint = '%s', pkeys = %s)" % (self.endpoint, self.pkeys)



class WampMessageUnprovide(WampMessage):
   """
   A WAMP Unprovide message.
   """

   MESSAGE_TYPE = 9
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, endpoint, pkeys = None):
      """
      Message constructor.

      :param endpoint: The WAMP or application URI of the RPC endpoint unprovided.
      :type endpoint: str
      :param pkeys: The endpoint is unprovided to work for this list of application partition keys.
      :type pkeys: list
      """
      WampMessage.__init__(self)
      self.endpoint = endpoint
      self.pkeys = pkeys


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageUnprovide.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise WampProtocolError("invalid message length %d for WAMP Unprovide message" % len(wmsg))

      ## topic
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'endpoint' in WAMP Unprovide message" % type(wmsg[1]))

      endpoint = parse_wamp_uri(wmsg[1])
      if endpoint is None:
         raise WampProtocolError("invalid URI '%s' for 'endpoint' in WAMP Unprovide message" % wmsg[1])

      ## options
      ##
      pkeys = None

      if len(wmsg) == 3:
         options = wmsg[2]

         if type(options) != dict:
            raise WampProtocolError("invalid type %s for 'options' in WAMP Unprovide message" % type(options))

         for k in options.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in 'options' in WAMP Unprovide message" % type(k))

         if options.has_key('pkeys'):

            option_pkeys = options['pkeys']
            if type(option_pkeys) != list:
               raise WampProtocolError("invalid type %s for 'pkeys' option in WAMP Unprovide message" % type(option_pkeys))

            for pk in option_pkeys:
               if type(pk) not in (str, unicode):
                  raise WampProtocolError("invalid type for value '%s' in 'pkeys' option in WAMP Unprovide message" % type(pk))

            pkeys = option_pkeys

      obj = Klass(endpoint, pkeys)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      options = {}

      if self.pkeys is not None:
         options['pkeys'] = self.pkeys

      if len(options):
         return [WampMessageUnprovide.MESSAGE_TYPE, self.endpoint, options]
      else:
         return [WampMessageUnprovide.MESSAGE_TYPE, self.endpoint]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Unprovide Message (endpoint = '%s', pkeys = %s)" % (self.endpoint, self.pkeys)



class WampMessageCall(WampMessage):
   """
   A WAMP Call message.
   """

   MESSAGE_TYPE = 10
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, callid, endpoint, args = [], sessionid = None, timeout = None):
      """
      Message constructor.

      :param callid: The WAMP call ID of the original call.
      :type callid: str
      :param endpoint: The WAMP or application URI of the RPC endpoint to be called.
      :type endpoint: str
      :param args: The (positional) arguments to be supplied for the parameters to the called endpoint.
      :type args: list
      :param sessionid: If present, restrict the callee to the given WAMP session ID.
      :type sessionid: str
      :param timeout: If present, let the callee automatically cancel the call after this ms.
      :type timeout: int
      """
      WampMessage.__init__(self)
      self.callid = callid
      self.endpoint = endpoint
      self.args = args
      self.sessionid = sessionid
      self.timeout = timeout


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageCall.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4, 5):
         raise WampProtocolError("invalid message length %d for WAMP Call message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'callid' in WAMP Call message" % type(wmsg[1]))

      callid = parse_wamp_callid(wmsg[1])
      if callid is None:
         raise WampProtocolError("invalid value '%s' for 'callid' in WAMP Call message" % wmsg[1])

      ## endpoint
      ##
      if type(wmsg[2]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'endpoint' in WAMP Call message" % type(wmsg[2]))

      endpoint = parse_wamp_uri(wmsg[2])
      if endpoint is None:
         raise WampProtocolError("invalid value '%s' for 'endpoint' in WAMP Call message" % wmsg[2])

      ## args
      ##
      args = []
      if len(wmsg) > 3:
         if type(wmsg[3]) != list:
            raise WampProtocolError("invalid type %s for 'arguments' in WAMP Call message" % type(wmsg[3]))
         args = wmsg[3]

      ## options
      ##
      sessionid = None
      timeout = None

      if len(wmsg) == 5:
         options = wmsg[4]

         if type(options) != dict:
            raise WampProtocolError("invalid type %s for 'options' in WAMP Call message" % type(options))

         for k in options.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in 'options' in WAMP Call message" % type(k))

         if options.has_key('session'):

            option_sessionid = options['session']
            if type(option_sessionid) not in (str, unicode):
               raise WampProtocolError("invalid type %s for 'session' option in WAMP Call message" % type(option_session))

            option_sessionid = parse_wamp_session(option_sessionid)
            if option_sessionid is None:
               raise WampProtocolError("invalid value %s for 'session' option in WAMP Call message" % options['session'])

            sessionid = option_sessionid

         if options.has_key('timeout'):

            option_timeout = options['timeout']
            if type(option_timeout) != int:
               raise WampProtocolError("invalid type %s for 'timeout' option in WAMP Call message" % type(option_timeout))

            if option_timeout < 0:
               raise WampProtocolError("invalid value %d for 'timeout' option in WAMP Call message" % option_timeout)

            timeout = option_timeout

      obj = Klass(callid, endpoint, args, sessionid = sessionid, timeout = timeout)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      options = {}

      if self.timeout is not None:
         options['timeout'] = self.timeout

      if self.sessionid is not None:
         options['session'] = self.sessionid

      if len(options):
         return [WampMessageCall.MESSAGE_TYPE, self.callid, self.endpoint, self.args, options]
      else:
         if len(self.args) > 0:
            return [WampMessageCall.MESSAGE_TYPE, self.callid, self.endpoint, self.args]
         else:
            return [WampMessageCall.MESSAGE_TYPE, self.callid, self.endpoint]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Call Message (callid = '%s', endpoint = '%s', args = %s, sessionid = '%s', timeout = %s)" % (self.callid, self.endpoint, self.args, self.sessionid, self.timeout)



class WampMessageCancelCall(WampMessage):
   """
   A WAMP Cancel-Call message.
   """

   MESSAGE_TYPE = 11
   """
   The WAMP message code for this type of message.
   """

   CANCEL_SKIP = 1
   CANCEL_ABORT = 2
   CANCEL_KILL = 3

   CANCEL_DESC = {
      CANCEL_SKIP: 'skip',
      CANCEL_ABORT: 'abort',
      CANCEL_KILL: 'kill'
   }


   def __init__(self, callid, mode = None):
      """
      Message constructor.

      :param callid: The WAMP call ID of the original call to cancel.
      :type callid: str
      :param mode: Specifies how to cancel the call (skip, abort or kill).
      :type mode: int
      """
      WampMessage.__init__(self)
      self.callid = callid
      self.mode = mode


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageCancelCall.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise WampProtocolError("invalid message length %d for WAMP Cancel-Call message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'callid' in WAMP Cancel-Call message" % type(wmsg[1]))

      callid = parse_wamp_callid(wmsg[1])
      if callid is None:
         raise WampProtocolError("invalid URI '%s' for 'callid' in WAMP Cancel-Call message" % wmsg[1])

      ## options
      ##
      mode = None

      if len(wmsg) == 3:
         options = wmsg[2]

         if type(options) != dict:
            raise WampProtocolError("invalid type %s for 'options' in WAMP Cancel-Call message" % type(options))

         for k in options.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in 'options' in WAMP Cancel-Call message" % type(k))

         if options.has_key('mode'):

            option_mode = options['mode']
            if type(option_mode) != int:
               raise WampProtocolError("invalid type %s for 'mode' option in WAMP Cancel-Call message" % type(option_mode))

            if option_moption_modeatch not in [WampMessageCancelCall.CANCEL_SKIP, WampMessageCancelCall.CANCEL_ABORT, WampMessageCancelCall.CANCEL_KILL]:
               raise WampProtocolError("invalid value %d for 'mode' option in WAMP Cancel-Call message" % option_mode)

            mode = option_mode

      obj = Klass(callid, mode = mode)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      options = {}

      if self.mode is not None:
         options['mode'] = self.mode

      if len(options):
         return [WampMessageCancelCall.MESSAGE_TYPE, self.callid, options]
      else:
         return [WampMessageCancelCall.MESSAGE_TYPE, self.callid]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Cancel-Call Message (callid = '%s', mode = %s)" % (self.callid, WampMessageCancelCall.CANCEL_DESC.get(self.mode))



class WampMessageCallProgress(WampMessage):
   """
   A WAMP Call-Progress message.
   """

   MESSAGE_TYPE = 12
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, callid, progress = None):
      """
      Message constructor.

      :param callid: The WAMP call ID of the original call this result is for.
      :type callid: str
      :param progress: Arbitrary application progress (must be serializable using the serializer in use).
      :type progress: any
      """
      WampMessage.__init__(self)
      self.callid = callid
      self.progress = progress


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageCallProgress.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise WampProtocolError("invalid message length %d for WAMP Call-Progress message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'callid' in WAMP Call-Progress message" % type(wmsg[1]))

      callid = parse_wamp_callid(wmsg[1])
      if callid is None:
         raise WampProtocolError("invalid value '%s' for 'callid' in WAMP Call-Progress message" % wmsg[1])

      ## result
      ##
      progress = None
      if len(wmsg) > 2:
         progress = wmsg[2]

      obj = Klass(callid, progress)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      if self.progress is not None:
         return [WampMessageCallProgress.MESSAGE_TYPE, self.callid, self.progress]
      else:
         return [WampMessageCallProgress.MESSAGE_TYPE, self.callid]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Call-Progress Message (callid = '%s', progress = %s)" % (self.callid, self.progress)



class WampMessageCallResult(WampMessage):
   """
   A WAMP Call-Result message.
   """

   MESSAGE_TYPE = 13
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, callid, result = None):
      """
      Message constructor.

      :param callid: The WAMP call ID of the original call this result is for.
      :type callid: str
      :param result: Arbitrary application result (must be serializable using the serializer in use).
      :type result: any
      """
      WampMessage.__init__(self)
      self.callid = callid
      self.result = result


   @classmethod
   def parse(Klass, wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list
      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageCallResult.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise WampProtocolError("invalid message length %d for WAMP Call-Result message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'callid' in WAMP Call-Result message" % type(wmsg[1]))

      callid = parse_wamp_callid(wmsg[1])
      if callid is None:
         raise WampProtocolError("invalid value '%s' for 'callid' in WAMP Call-Result message" % wmsg[1])

      ## result
      ##
      result = None
      if len(wmsg) > 2:
         result = wmsg[2]

      obj = Klass(callid, result)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      if self.result is not None:
         return [WampMessageCallResult.MESSAGE_TYPE, self.callid, self.result]
      else:
         return [WampMessageCallResult.MESSAGE_TYPE, self.callid]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Call-Result Message (callid = '%s', result = %s)" % (self.callid, self.result)



class WampMessageCallError(WampMessageError):
   """
   A WAMP Call-Error message.
   """

   MESSAGE_TYPE = 14
   """
   The WAMP message code for this type of message.
   """


