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

from __future__ import absolute_import

import urlparse, urllib

from autobahn.wamp.exception import ProtocolError



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


def check_or_raise_uri(value, message):
   if type(value) not in [str, unicode]:
      raise ProtocolError("{}: invalid type {} for URI".format(message, type(value)))
   if len(value) == 0:
      raise ProtocolError("{}: invalid value '{}' for URI".format(message, value))
   return value


def check_or_raise_id(value, message):
   if type(value) != int:
      raise ProtocolError("{}: invalid type {} for ID".format(message, type(value)))
   if value < 0 or value > 9007199254740992: # 2**53
      raise ProtocolError("{}: invalid value {} for ID".format(message, value))
   return value


def check_or_raise_dict(value, message):
   if type(value) != dict:
      raise ProtocolError("{}: invalid type {}".format(message, type(value)))
   for k in value.keys():
      if type(k) not in (str, unicode):
         raise ProtocolError("{}: invalid type {} for key '{}'".format(type(k), k))
   return value



def parse_wamp_sessionid(string):
   ## FIXME: verify/parse WAMP session ID
   return string



def parse_wamp_callid(string):
   ## FIXME: verify/parse WAMP call ID
   return string



class Message:
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
         #print "Message.serialize [new]", serializer
         self._serialized[serializer] = serializer.serialize(self.marshal())
      else:
         #print "Message.serialize [cached]", serializer
         pass

      return self._serialized[serializer]

   def __eq__(self, other):
      return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

   def __ne__(self, other):
      return not self.__eq__(other)



class Error(Message):
   """
   A WAMP `ERROR` message.

   Formats:
     * `[ERROR, REQUEST.Request|id, Details|dict, Error|uri]`
     * `[ERROR, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list]`
     * `[ERROR, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list, ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 17
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request, error, args = None, kwargs = None):
      """
      Message constructor.

      :param request: The WAMP request ID of the original request (`Call`, `Subscribe`, ...) this error occured for.
      :type request: int
      :param error: The WAMP or application error URI for the error that occured.
      :type error: str
      :param args: Positional values for application-defined exception.
                   Must be serializable using any serializers in use.
      :type args: list
      :param kwargs: Keyword values for application-defined exception.
                     Must be serializable using any serializers in use.
      :type kwargs: dict
      """
      assert(not (kwargs and not args))
      Message.__init__(self)
      self.request = request
      self.error = error
      self.args = args
      self.kwargs = kwargs


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

      if len(wmsg) not in (4, 5, 6):
         raise ProtocolError("invalid message length {} for ERROR".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in ERROR")
      details = check_or_raise_dict(wmsg[2], "'details' in ERROR")
      error = check_or_raise_uri(wmsg[3], "'error' in ERROR")

      args = None
      if len(wmsg) > 4:
         args = wmsg[4]
         if type(args) != list:
            raise ProtocolError("invalid type {} for 'args' in ERROR".format(type(args)))

      kwargs = None
      if len(wmsg) > 5:
         kwargs = wmsg[5]
         if type(kwargs) != dict:
            raise ProtocolError("invalid type {} for 'kwargs' in ERROR".format(type(kwargs)))

      obj = Klass(request, error, args = args, kwargs = kwargs)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      details = {}

      if self.kwargs:
         return [self.MESSAGE_TYPE, self.request, details, self.error, self.args, self.kwargs]
      elif self.args:
         return [self.MESSAGE_TYPE, self.request, details, self.error, self.args]
      else:
         return [self.MESSAGE_TYPE, self.request, details, self.error]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Error Message (request = {}, error = {}, exception = {}, exceptionkw = {})".format(self.request, self.error, self.exception, self.exceptionkw)



class Subscribe(Message):
   """
   A WAMP `SUBSCRIBE` message.

   Format: `[SUBSCRIBE, Request|id, Options|dict, Topic|uri]`
   """

   MESSAGE_TYPE = 3
   """
   The WAMP message code for this type of message.
   """

   MATCH_EXACT = 'exact'
   MATCH_PREFIX = 'prefix'
   MATCH_WILDCARD = 'wildcard'

   def __init__(self, request, topic, match = MATCH_EXACT):
      """
      Message constructor.

      :param request: The WAMP request ID of this request.
      :type request: int
      :param topic: The WAMP or application URI of the PubSub topic to subscribe to.
      :type topic: str
      :param match: The topic matching method to be used for the subscription.
      :type match: int
      """
      Message.__init__(self)
      self.request = request
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
      assert(len(wmsg) > 0 and wmsg[0] == Subscribe.MESSAGE_TYPE)

      if len(wmsg) != 4:
         raise ProtocolError("invalid message length %d for SUBSCRIBE" % len(wmsg))

      request = check_or_raise_id(wmsg[1], "'request' in SUBSCRIBE")
      options = check_or_raise_dict(wmsg[2], "'options' in SUBSCRIBE")
      topic = check_or_raise_uri(wmsg[3], "'topic' in SUBSCRIBE")

      match = Subscribe.MATCH_EXACT

      if options.has_key('match'):

         option_match = options['match']
         if type(option_match) not in [str, unicode]:
            raise ProtocolError("invalid type {} for 'match' option in SUBSCRIBE".format(type(option_match)))

         if option_match not in [Subscribe.MATCH_EXACT, Subscribe.MATCH_PREFIX, Subscribe.MATCH_WILDCARD]:
            raise ProtocolError("invalid value {} for 'match' option in SUBSCRIBE".format(option_match))

         match = option_match

      obj = Klass(request, topic, match)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      options = {}

      if self.match != Subscribe.MATCH_EXACT:
         options['match'] = self.match

      return [Subscribe.MESSAGE_TYPE, self.request, options, self.topic]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP SUBSCRIBE Message (request = {}, topic = {}, match = {})".format(self.request, self.topic, self.match)



class Subscribed(Message):
   """
   A WAMP `SUBSCRIBED` message.

   Format: `[SUBSCRIBED, SUBSCRIBE.Request|id, Subscription|id]`
   """

   MESSAGE_TYPE = 103
   """
   The WAMP message code for this type of message.
   """

   def __init__(self, request, subscription):
      """
      Message constructor.

      :param request: The request ID of the original `SUBSCRIBE` request.
      :type request: int
      :param subscription: The subscription ID for the subscribed topic (or topic pattern).
      :type subscription: int
      """
      Message.__init__(self)
      self.request = request
      self.subscription = subscription


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
      assert(len(wmsg) > 0 and wmsg[0] == Subscribed.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for SUBSCRIBED".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in SUBSCRIBED")
      subscription = check_or_raise_id(wmsg[2], "'subscription' in SUBSCRIBED")

      obj = Klass(request, subscription)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [Subscribed.MESSAGE_TYPE, self.request, self.subscription]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP SUBSCRIBED Message (request = {}, subscription = {})".format(self.request, self.subscription)



class Unsubscribe(Message):
   """
   A WAMP `UNSUBSCRIBE` message.

   Format: `[UNSUBSCRIBE, Request|id, SUBSCRIBED.Subscription|id]`
   """

   MESSAGE_TYPE = 4
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request, subscription):
      """
      Message constructor.

      :param request: The WAMP request ID of this request.
      :type request: int
      :param subscription: The subscription ID for the subscription to unsubscribe from.
      :type subscription: int
      """
      Message.__init__(self)
      self.request = request
      self.subscription = subscription


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
      assert(len(wmsg) > 0 and wmsg[0] == Unsubscribe.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for WAMP UNSUBSCRIBE".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in UNSUBSCRIBE")
      subscription = check_or_raise_id(wmsg[2], "'subscription' in UNSUBSCRIBE")

      obj = Klass(request, subscription)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [Unsubscribe.MESSAGE_TYPE, self.request, self.subscription]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP UNSUBSCRIBE Message (request = {}, subscription = {})".format(self.request, self.subscription)



class Unsubscribed(Message):
   """
   A WAMP `UNSUBSCRIBED` message.

   Format: `[UNSUBSCRIBED, UNSUBSCRIBE.Request|id]`
   """

   MESSAGE_TYPE = 153
   """
   The WAMP message code for this type of message.
   """

   def __init__(self, request):
      """
      Message constructor.

      :param request: The request ID of the original `UNSUBSCRIBE` request.
      :type request: int
      """
      Message.__init__(self)
      self.request = request


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
      assert(len(wmsg) > 0 and wmsg[0] == Unsubscribed.MESSAGE_TYPE)

      if len(wmsg) != 2:
         raise ProtocolError("invalid message length {} for UNSUBSCRIBED".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in UNSUBSCRIBED")

      obj = Klass(request)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [Unsubscribed.MESSAGE_TYPE, self.request]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP UNSUBSCRIBED Message (request = {})".format(self.request)



class Publish(Message):
   """
   A WAMP `PUBLISH` message.

   Formats:
     * `[PUBLISH, Request|id, Options|dict, Topic|uri]`
     * `[PUBLISH, Request|id, Options|dict, Topic|uri, Arguments|list]`
     * `[PUBLISH, Request|id, Options|dict, Topic|uri, Arguments|list, ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 5
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request, topic, args = None, kwargs = None, excludeMe = None, exclude = None, eligible = None, discloseMe = None):
      """
      Message constructor.

      :param topic: The WAMP or application URI of the PubSub topic the event should
                    be published to.
      :type topic: str
      :param args: Positional values for application-defined event payload.
                   Must be serializable using any serializers in use.
      :type args: list
      :param kwargs: Keyword values for application-defined event payload.
                     Must be serializable using any serializers in use.
      :param excludeMe: If True, exclude the publisher from receiving the event, even
                        if he is subscribed (and eligible).
      :type excludeMe: bool
      :param exclude: List of WAMP session IDs to exclude from receiving this event.
      :type exclude: list
      :param eligible: List of WAMP session IDs eligible to receive this event.
      :type eligible: list
      :param discloseMe: If True, request to disclose the publisher of this event
                         to subscribers.
      :type discloseMe: bool
      """
      assert(not (kwargs and not args))
      Message.__init__(self)
      self.request = request
      self.topic = topic
      self.args = args
      self.kwargs = kwargs
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
      assert(len(wmsg) > 0 and wmsg[0] == Publish.MESSAGE_TYPE)

      if len(wmsg) not in (4, 5, 6):
         raise ProtocolError("invalid message length {} for PUBLISH".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in PUBLISH")
      options = check_or_raise_dict(wmsg[2], "'options' in PUBLISH")
      topic = check_or_raise_uri(wmsg[3], "'topic' in PUBLISH")

      args = None
      if len(wmsg) > 4:
         args = wmsg[4]
         if type(args) != list:
            raise ProtocolError("invalid type {} for 'args' in PUBLISH".format(type(args)))

      kwargs = None
      if len(wmsg) > 5:
         kwargs = wmsg[5]
         if type(kwargs) != dict:
            raise ProtocolError("invalid type {} for 'kwargs' in PUBLISH".format(type(kwargs)))

      excludeMe = None
      exclude = None
      eligible = None
      discloseMe = None

      if options.has_key('excludeme'):

         option_excludeMe = options['excludeme']
         if type(option_excludeMe) != bool:
            raise ProtocolError("invalid type {} for 'excludeme' option in PUBLISH".format(type(option_excludeMe)))

         excludeMe = option_excludeMe

      if options.has_key('exclude'):

         option_exclude = options['exclude']
         if type(option_exclude) != list:
            raise ProtocolError("invalid type {} for 'exclude' option in PUBLISH".format(type(option_exclude)))

         for sessionId in option_exclude:
            if type(sessionId) != int:
               raise ProtocolError("invalid type {} for value in 'exclude' option in PUBLISH".format(type(sessionId)))

         exclude = option_exclude

      if options.has_key('eligible'):

         option_eligible = options['eligible']
         if type(option_eligible) != list:
            raise ProtocolError("invalid type {} for 'eligible' option in PUBLISH".format(type(option_eligible)))

         for sessionId in option_eligible:
            if type(sessionId) != int:
               raise ProtocolError("invalid type {} for value in 'eligible' option in PUBLISH".format(type(sessionId)))

         eligible = option_eligible

      if options.has_key('discloseme'):

         option_discloseMe = options['discloseme']
         if type(option_discloseMe) != bool:
            raise ProtocolError("invalid type {} for 'discloseme' option in PUBLISH".format(type(option_identifyMe)))

         discloseMe = option_discloseMe

      obj = Klass(request, topic, args = args, kwargs = kwargs, excludeMe = excludeMe, exclude = exclude, eligible = eligible, discloseMe = discloseMe)

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

      if self.kwargs:
         return [Publish.MESSAGE_TYPE, self.request, options, self.topic, self.args, self.kwargs]
      elif self.args:
         return [Publish.MESSAGE_TYPE, self.request, options, self.topic, self.args]
      else:
         return [Publish.MESSAGE_TYPE, self.request, options, self.topic]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP PUBLISH Message (request = {}, topic = {}, args = {}, kwargs = {}, excludeMe = {}, exclude = {}, eligible = {}, discloseMe = {})" % (self.request, self.topic, self.args, self.kwargs, self.excludeMe, self.exclude, self.eligible, self.discloseMe)



class Event(Message):
   """
   A WAMP `EVENT` message.

   Formats:

     * `[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict]`
     * `[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list]`
     * `[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list, PUBLISH.ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 6
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, subscription, publication, args = None, kwargs = None, publisher = None):
      """
      Message constructor.

      :param subscription: The subscription ID this event is dispatched under.
      :type subscription: int
      :param publication: The publication ID of the dispatched event.
      :type publication: int
      :param args: Positional values for application-defined exception.
                   Must be serializable using any serializers in use.
      :type args: list
      :param kwargs: Keyword values for application-defined exception.
                     Must be serializable using any serializers in use.
      :type kwargs: dict
      :param publisher: If present, the WAMP session ID of the publisher of this event.
      :type publisher: str
      """
      assert(not (kwargs and not args))
      Message.__init__(self)
      self.subscription = subscription
      self.publication = publication
      self.args = args
      self.kwargs = kwargs
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
      assert(len(wmsg) > 0 and wmsg[0] == Event.MESSAGE_TYPE)

      if len(wmsg) not in (4, 5, 6):
         raise ProtocolError("invalid message length {} for EVENT".format(len(wmsg)))

      subscription = check_or_raise_id(wmsg[1], "'subscription' in EVENT")
      publication = check_or_raise_id(wmsg[2], "'publication' in EVENT")
      details = check_or_raise_dict(wmsg[3], "'details' in EVENT")

      args = None
      if len(wmsg) > 4:
         args = wmsg[4]
         if type(args) != list:
            raise ProtocolError("invalid type %s for 'args' in EVENT" % type(args))

      kwargs = None
      if len(wmsg) > 5:
         kwargs = wmsg[5]
         if type(kwargs) != dict:
            raise ProtocolError("invalid type %s for 'kwargs' in EVENT" % type(kwargs))

      publisher = None

      if details.has_key('publisher'):

         detail_publisher = details['publisher']
         if type(detail_publisher) != int:
            raise ProtocolError("invalid type {} for 'publisher' detail in EVENT".format(type(detail_publisher)))

         publisher = detail_publisher

      obj = Klass(subscription, publication, args = args, kwargs = kwargs, publisher = publisher)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      details = {}

      if self.publisher is not None:
         details['publisher'] = self.publisher

      if self.kwargs:
         return [Event.MESSAGE_TYPE, self.subscription, self.publication, details, self.args, self.kwargs]
      elif self.args:
         return [Event.MESSAGE_TYPE, self.subscription, self.publication, details, self.args]
      else:
         return [Event.MESSAGE_TYPE, self.subscription, self.publication, details]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP EVENT Message (subscription = {}, publication = {}, args = {}, kwargs = {}, publisher = {})".format(self.subscription, self.publication, self.args, self.kwargs, self.publisher)



class MetaEvent(Message):
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
      Message.__init__(self)
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
      assert(len(wmsg) > 0 and wmsg[0] == MetaEvent.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4):
         raise ProtocolError("invalid message length %d for WAMP Meta-Event message" % len(wmsg))

      ## topic
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise ProtocolError("invalid type %s for 'topic' in WAMP Meta-Event message" % type(wmsg[1]))

      topic = parse_wamp_uri(wmsg[1])
      if topic is None:
         raise ProtocolError("invalid URI '%s' for 'topic' in WAMP Meta-Event message" % wmsg[1])

      ## metatopic
      ##
      if type(wmsg[2]) not in (str, unicode):
         raise ProtocolError("invalid type %s for 'metatopic' in WAMP Meta-Event message" % type(wmsg[2]))

      metatopic = parse_wamp_uri(wmsg[2])
      if metatopic is None:
         raise ProtocolError("invalid URI '%s' for 'metatopic' in WAMP Meta-Event message" % wmsg[2])

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
         return [MetaEvent.MESSAGE_TYPE, self.topic, self.metatopic, self.metaevent]
      else:
         return [MetaEvent.MESSAGE_TYPE, self.topic, self.metatopic]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Meta-Event Message (topic = '%s', metatopic = '%s', metaevent = %s)" % (self.topic, self.metatopic, self.metaevent)



class Register(Message):
   """
   A WAMP `REGISTER` message.

   Format: `[REGISTER, Request|id, Options|dict, Procedure|uri]`
   """

   MESSAGE_TYPE = 8
   """
   The WAMP message code for this type of message.
   """

   def __init__(self, request, procedure, pkeys = None):
      """
      Message constructor.

      :param request: The WAMP request ID of this request.
      :type request: int
      :param procedure: The WAMP or application URI of the RPC endpoint provided.
      :type procedure: str
      :param pkeys: The endpoint can work for this list of application partition keys.
      :type pkeys: list
      """
      Message.__init__(self)
      self.request = request
      self.procedure = procedure
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
      assert(len(wmsg) > 0 and wmsg[0] == Register.MESSAGE_TYPE)

      if len(wmsg) != 4:
         raise ProtocolError("invalid message length {} for REGISTER".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in REGISTER")
      options = check_or_raise_dict(wmsg[2], "'options' in REGISTER")
      procedure = check_or_raise_uri(wmsg[3], "'procedure' in REGISTER")

      pkeys = None

      if options.has_key('pkeys'):

         option_pkeys = options['pkeys']
         if type(option_pkeys) != list:
            raise ProtocolError("invalid type {} for 'pkeys' option in REGISTER".format(type(option_pkeys)))

         for pk in option_pkeys:
            if type(pk) != int:
               raise ProtocolError("invalid type for value '{}' in 'pkeys' option in REGISTER".format(type(pk)))

         pkeys = option_pkeys

      obj = Klass(request, procedure, pkeys = pkeys)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      options = {}

      if self.pkeys is not None:
         options['pkeys'] = self.pkeys

      return [Register.MESSAGE_TYPE, self.request, options, self.procedure]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP REGISTER Message (request = {}, procedure = {}, pkeys = {})".format(self.request, self.procedure, self.pkeys)



class Registered(Message):
   """
   A WAMP `REGISTERED` message.

   Format: `[REGISTERED, REGISTER.Request|id, Registration|id]`
   """

   MESSAGE_TYPE = 103
   """
   The WAMP message code for this type of message.
   """

   def __init__(self, request, registration):
      """
      Message constructor.

      :param request: The request ID of the original `REGISTER` request.
      :type request: int
      :param subscription: The registration ID for the registered procedure (or procedure pattern).
      :type subscription: int
      """
      Message.__init__(self)
      self.request = request
      self.registration = registration


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
      assert(len(wmsg) > 0 and wmsg[0] == Registered.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for REGISTERED".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in REGISTERED")
      registration = check_or_raise_id(wmsg[2], "'registration' in REGISTERED")

      obj = Klass(request, registration)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [Registered.MESSAGE_TYPE, self.request, self.registration]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP REGISTERED Message (request = {}, registration = {})".format(self.request, self.registration)



class Unregister(Message):
   """
   A WAMP Unprovide message.

   Format: `[UNREGISTER, Request|id, REGISTERED.Registration|id]`
   """

   MESSAGE_TYPE = 9
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request, registration):
      """
      Message constructor.

      :param request: The WAMP request ID of this request.
      :type request: int
      :param registration: The registration ID for the registration to unregister.
      :type registration: int
      """
      Message.__init__(self)
      self.request = request
      self.registration = registration


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
      assert(len(wmsg) > 0 and wmsg[0] == Unregister.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for WAMP UNREGISTER".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in UNREGISTER")
      registration = check_or_raise_id(wmsg[2], "'registration' in UNREGISTER")

      obj = Klass(request, registration)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [Unregister.MESSAGE_TYPE, self.request, self.registration]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP UNREGISTER Message (request = {}, registration = {})".format(self.request, self.registration)



class Unregistered(Message):
   """
   A WAMP `UNREGISTERED` message.

   Format: `[UNREGISTERED, UNREGISTER.Request|id]`
   """

   MESSAGE_TYPE = 153
   """
   The WAMP message code for this type of message.
   """

   def __init__(self, request):
      """
      Message constructor.

      :param request: The request ID of the original `UNREGISTER` request.
      :type request: int
      """
      Message.__init__(self)
      self.request = request


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
      assert(len(wmsg) > 0 and wmsg[0] == Unregistered.MESSAGE_TYPE)

      if len(wmsg) != 2:
         raise ProtocolError("invalid message length {} for UNREGISTER".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in UNREGISTER")

      obj = Klass(request)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [Unregistered.MESSAGE_TYPE, self.request]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP UNREGISTER Message (request = {})".format(self.request)



class Call(Message):
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
      Message.__init__(self)
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
      assert(len(wmsg) > 0 and wmsg[0] == Call.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4, 5):
         raise ProtocolError("invalid message length %d for WAMP Call message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise ProtocolError("invalid type %s for 'callid' in WAMP Call message" % type(wmsg[1]))

      callid = parse_wamp_callid(wmsg[1])
      if callid is None:
         raise ProtocolError("invalid value '%s' for 'callid' in WAMP Call message" % wmsg[1])

      ## endpoint
      ##
      if type(wmsg[2]) not in (str, unicode):
         raise ProtocolError("invalid type %s for 'endpoint' in WAMP Call message" % type(wmsg[2]))

      endpoint = parse_wamp_uri(wmsg[2])
      if endpoint is None:
         raise ProtocolError("invalid value '%s' for 'endpoint' in WAMP Call message" % wmsg[2])

      ## args
      ##
      args = []
      if len(wmsg) > 3:
         if type(wmsg[3]) != list:
            raise ProtocolError("invalid type %s for 'arguments' in WAMP Call message" % type(wmsg[3]))
         args = wmsg[3]

      ## options
      ##
      sessionid = None
      timeout = None

      if len(wmsg) == 5:
         options = wmsg[4]

         if type(options) != dict:
            raise ProtocolError("invalid type %s for 'options' in WAMP Call message" % type(options))

         for k in options.keys():
            if type(k) not in (str, unicode):
               raise ProtocolError("invalid type %s for key in 'options' in WAMP Call message" % type(k))

         if options.has_key('session'):

            option_sessionid = options['session']
            if type(option_sessionid) not in (str, unicode):
               raise ProtocolError("invalid type %s for 'session' option in WAMP Call message" % type(option_session))

            option_sessionid = parse_wamp_session(option_sessionid)
            if option_sessionid is None:
               raise ProtocolError("invalid value %s for 'session' option in WAMP Call message" % options['session'])

            sessionid = option_sessionid

         if options.has_key('timeout'):

            option_timeout = options['timeout']
            if type(option_timeout) != int:
               raise ProtocolError("invalid type %s for 'timeout' option in WAMP Call message" % type(option_timeout))

            if option_timeout < 0:
               raise ProtocolError("invalid value %d for 'timeout' option in WAMP Call message" % option_timeout)

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
         return [Call.MESSAGE_TYPE, self.callid, self.endpoint, self.args, options]
      else:
         if len(self.args) > 0:
            return [Call.MESSAGE_TYPE, self.callid, self.endpoint, self.args]
         else:
            return [Call.MESSAGE_TYPE, self.callid, self.endpoint]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Call Message (callid = '%s', endpoint = '%s', args = %s, sessionid = '%s', timeout = %s)" % (self.callid, self.endpoint, self.args, self.sessionid, self.timeout)



class CancelCall(Message):
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
      Message.__init__(self)
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
      assert(len(wmsg) > 0 and wmsg[0] == CancelCall.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise ProtocolError("invalid message length %d for WAMP Cancel-Call message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise ProtocolError("invalid type %s for 'callid' in WAMP Cancel-Call message" % type(wmsg[1]))

      callid = parse_wamp_callid(wmsg[1])
      if callid is None:
         raise ProtocolError("invalid URI '%s' for 'callid' in WAMP Cancel-Call message" % wmsg[1])

      ## options
      ##
      mode = None

      if len(wmsg) == 3:
         options = wmsg[2]

         if type(options) != dict:
            raise ProtocolError("invalid type %s for 'options' in WAMP Cancel-Call message" % type(options))

         for k in options.keys():
            if type(k) not in (str, unicode):
               raise ProtocolError("invalid type %s for key in 'options' in WAMP Cancel-Call message" % type(k))

         if options.has_key('mode'):

            option_mode = options['mode']
            if type(option_mode) != int:
               raise ProtocolError("invalid type %s for 'mode' option in WAMP Cancel-Call message" % type(option_mode))

            if option_moption_modeatch not in [CancelCall.CANCEL_SKIP, CancelCall.CANCEL_ABORT, CancelCall.CANCEL_KILL]:
               raise ProtocolError("invalid value %d for 'mode' option in WAMP Cancel-Call message" % option_mode)

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
         return [CancelCall.MESSAGE_TYPE, self.callid, options]
      else:
         return [CancelCall.MESSAGE_TYPE, self.callid]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Cancel-Call Message (callid = '%s', mode = %s)" % (self.callid, CancelCall.CANCEL_DESC.get(self.mode))



class CallProgress(Message):
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
      Message.__init__(self)
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
      assert(len(wmsg) > 0 and wmsg[0] == CallProgress.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise ProtocolError("invalid message length %d for WAMP Call-Progress message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise ProtocolError("invalid type %s for 'callid' in WAMP Call-Progress message" % type(wmsg[1]))

      callid = parse_wamp_callid(wmsg[1])
      if callid is None:
         raise ProtocolError("invalid value '%s' for 'callid' in WAMP Call-Progress message" % wmsg[1])

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
         return [CallProgress.MESSAGE_TYPE, self.callid, self.progress]
      else:
         return [CallProgress.MESSAGE_TYPE, self.callid]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Call-Progress Message (callid = '%s', progress = %s)" % (self.callid, self.progress)



class CallResult(Message):
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
      Message.__init__(self)
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
      assert(len(wmsg) > 0 and wmsg[0] == CallResult.MESSAGE_TYPE)

      if len(wmsg) not in (2, 3):
         raise ProtocolError("invalid message length %d for WAMP Call-Result message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise ProtocolError("invalid type %s for 'callid' in WAMP Call-Result message" % type(wmsg[1]))

      callid = parse_wamp_callid(wmsg[1])
      if callid is None:
         raise ProtocolError("invalid value '%s' for 'callid' in WAMP Call-Result message" % wmsg[1])

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
         return [CallResult.MESSAGE_TYPE, self.callid, self.result]
      else:
         return [CallResult.MESSAGE_TYPE, self.callid]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Call-Result Message (callid = '%s', result = %s)" % (self.callid, self.result)



class CallError(Error):
   """
   A WAMP Call-Error message.
   """

   MESSAGE_TYPE = 14
   """
   The WAMP message code for this type of message.
   """



class Hello(Message):
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
      Message.__init__(self)
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
      assert(len(wmsg) > 0 and wmsg[0] == Hello.MESSAGE_TYPE)

      if len(wmsg) != 2:
         raise ProtocolError("invalid message length %d for WAMP Hello message" % len(wmsg))

      ## sessionid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise ProtocolError("invalid type %s for 'sessionid' in WAMP Hello message" % type(wmsg[1]))

      sessionid = parse_wamp_sessionid(wmsg[1])
      if sessionid is None:
         raise ProtocolError("invalid value '%s' for 'sessionid' in WAMP Hello message" % wmsg[1])

      obj = Klass(sessionid)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [Hello.MESSAGE_TYPE, self.sessionid]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Hello Message (sessionid = '%s')" % (self.sessionid)



class RoleChange(Message):
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
      Message.__init__(self)
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
      assert(len(wmsg) > 0 and wmsg[0] == RoleChange.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length %d for WAMP Role-Change message" % len(wmsg))

      ## op
      ##
      op = wmsg[1]
      if type(op) != int:
         raise ProtocolError("invalid type %s for 'op' in WAMP Role-Change message" % type(op))
      if op not in [RoleChange.ROLE_CHANGE_OP_ADD, RoleChange.ROLE_CHANGE_OP_REMOVE]:
         raise ProtocolError("invalid value '%s' for 'op' in WAMP Role-Change message" % op)

      ## role
      ##
      role = wmsg[2]
      if type(role) not in (str, unicode):
         raise ProtocolError("invalid type %s for 'role' in WAMP Role-Change message" % type(role))
      if role not in [RoleChange.ROLE_CHANGE_ROLE_BROKER, RoleChange.ROLE_CHANGE_ROLE_DEALER]:
         raise ProtocolError("invalid value '%s' for 'role' in WAMP Role-Change message" % role)

      obj = Klass(op, role)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [RoleChange.MESSAGE_TYPE, self.op, self.role]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Role-Change Message (op = '%s', role = '%s')" % (RoleChange.ROLE_CHANGE_OP_DESC.get(self.op), self.role)



class Heartbeat(Message):
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
      Message.__init__(self)
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
      assert(len(wmsg) > 0 and wmsg[0] == Heartbeat.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length %d for WAMP Heartbeat message" % len(wmsg))

      ## incoming
      ##
      incoming = wmsg[1]

      if type(incoming) != int:
         raise ProtocolError("invalid type %s for 'incoming' in WAMP Heartbeat message" % type(incoming))

      if incoming < 0: # must be non-negative
         raise ProtocolError("invalid value %d for 'incoming' in WAMP Heartbeat message" % incoming)

      ## outgoing
      ##
      outgoing = wmsg[2]

      if type(outgoing) != int:
         raise ProtocolError("invalid type %s for 'outgoing' in WAMP Heartbeat message" % type(outgoing))

      if outgoing <= 0: # must be positive
         raise ProtocolError("invalid value %d for 'outgoing' in WAMP Heartbeat message" % outgoing)

      obj = Klass(incoming, outgoing)

      return obj

   
   def marshal(self):
      """
      Marshal this object into a raw message for subsequent serialization to bytes.
      """
      return [Heartbeat.MESSAGE_TYPE, self.incoming, self.outgoing]


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Hearbeat Message (incoming %d, outgoing = %d)" % (self.incoming, self.outgoing)



