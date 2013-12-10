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



class WampMessageSubscribe(WampMessage):
   """
   A WAMP Subscribe message.
   """

   MESSAGE_TYPE = 64 + 0
   """
   The WAMP message code for this type of message.
   """

   MATCH_EXACT = 1
   MATCH_PREFIX = 2
   MATCH_WILDCARD = 3

   MATCH_DESC = {MATCH_EXACT: 'exact', MATCH_PREFIX: 'prefix', MATCH_WILDCARD: 'wildcard'}


   def __init__(self, topic, match = MATCH_EXACT):
      """
      Message constructor.

      :param topic: The WAMP or application URI of the PubSub topic to subscribe to.
      :type topic: str
      :param match: The topic matching method to be used for the subscription.
      :type match: int
      """
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

      if len(wmsg) not in (2, 3):
         raise WampProtocolError("invalid message length %d for WAMP Subscribe message" % len(wmsg))

      ## topic
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for topic in WAMP Subscribe message" % type(wmsg[1]))

      topic = parse_wamp_uri(wmsg[1])
      if topic is None:
         raise WampProtocolError("invalid URI '%s' for topic in WAMP Subscribe message" % wmsg[1])

      ## options
      ##
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
      """
      Serialize this object into a wire level bytestring representation.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`
      """
      options = {}

      if self.match != WampMessageSubscribe.MATCH_EXACT:
         options['match'] = self.match

      if len(options):
         return serializer.serialize([self.MESSAGE_TYPE, self.topic, options])
      else:
         return serializer.serialize([self.MESSAGE_TYPE, self.topic])


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Subscribe Message (topic = '%s', match = %s)" % (self.topic, WampMessageSubscribe.MATCH_DESC.get(self.match))



class WampMessageUnsubscribe(WampMessage):
   """
   A WAMP Unsubscribe message.
   """

   MESSAGE_TYPE = 64 + 1
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

   
   def serialize(self, serializer):
      """
      Serialize this object into a wire level bytestring representation.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`
      """
      options = {}

      if self.match != WampMessageSubscribe.MATCH_EXACT:
         options['match'] = self.match

      if len(options):
         return serializer.serialize([WampMessageUnsubscribe.MESSAGE_TYPE, self.topic, options])
      else:
         return serializer.serialize([WampMessageUnsubscribe.MESSAGE_TYPE, self.topic])


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

   MESSAGE_TYPE = 64 + 2
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

   
   def serialize(self, serializer):
      """
      Serialize this object into a wire level bytestring representation.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`
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
         return serializer.serialize([WampMessagePublish.MESSAGE_TYPE, self.topic, self.event, options])
      else:
         return serializer.serialize([WampMessagePublish.MESSAGE_TYPE, self.topic, self.event])


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

   MESSAGE_TYPE = 64 + 3
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, topic, event = None, publisher = None):
      """
      Message constructor.

      :param topic: The WAMP or application URI of the PubSub topic the event was published to.
      :type topic: str
      :param event: Arbitrary application event payload (must be serializable using the serializer in use).
      :type event: any
      :param publisher: If present, the WAMP session ID of the publisher of this event.
      :type publisher: str
      """
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

      if len(wmsg) not in (2, 3, 4):
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
      event = None
      if len(wmsg) > 2:
         event = wmsg[2]

      ## details
      ##
      publisher = None

      if len(wmsg) == 4:
         details = wmsg[3]

         if type(details) != dict:
            raise WampProtocolError("invalid type %s for 'details' in WAMP Publish message" % type(details))

         for k in details.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in 'details' in WAMP Publish message" % type(k))

         if details.has_key('publisher'):

            detail_publisher = details['publisher']
            if type(detail_publisher) not in (str, unicode):
               raise WampProtocolError("invalid type %s for 'publisher' detail in WAMP Publish message" % type(detail_publisher))

            publisher = detail_publisher

      obj = Klass(topic, event, publisher)

      return obj

   
   def serialize(self, serializer):
      """
      Serialize this object into a wire level bytestring representation.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`
      """
      details = {}

      if self.publisher is not None:
         details['publisher'] = publisher

      if len(details):
         return serializer.serialize([WampMessagePublish.MESSAGE_TYPE, self.topic, self.event, details])
      else:
         if self.event is not None:
            return serializer.serialize([WampMessagePublish.MESSAGE_TYPE, self.topic, self.event])
         else:
            return serializer.serialize([WampMessagePublish.MESSAGE_TYPE, self.topic])


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Publish Message (topic = '%s', event = %s, publisher = %s)" % (self.topic, self.event, self.publisher)



class WampMessageCall(WampMessage):
   """
   A WAMP Call message.
   """

   MESSAGE_TYPE = 64 + 4
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
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageEvent.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4, 5):
         raise WampProtocolError("invalid message length %d for WAMP Call message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'callid' in WAMP Call message" % type(wmsg[1]))

      callid = parse_wamp_callid(wmsg[1])
      if callid is None:
         raise WampProtocolError("invalid URI '%s' for 'callid' in WAMP Call message" % wmsg[1])

      ## endpoint
      ##
      if type(wmsg[2]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'endpoint' in WAMP Call message" % type(wmsg[2]))

      endpoint = parse_wamp_uri(wmsg[2])
      if endpoint is None:
         raise WampProtocolError("invalid URI '%s' for 'endpoint' in WAMP Call message" % wmsg[2])

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

   
   def serialize(self, serializer):
      """
      Serialize this object into a wire level bytestring representation.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`
      """
      options = {}

      if self.timeout is not None:
         options['timeout'] = timeout

      if self.session is not None:
         options['session'] = sessionid

      if len(options):
         return serializer.serialize([WampMessageCall.MESSAGE_TYPE, self.callid, self.endpoint, self.args, options])
      else:
         if len(self.args) > 0:
            return serializer.serialize([WampMessageCall.MESSAGE_TYPE, self.callid, self.endpoint, self.args])
         else:
            return serializer.serialize([WampMessageCall.MESSAGE_TYPE, self.callid, self.endpoint])


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Call Message (callid = '%s', endpoint = '%s', args = %s, sessionid = '%s', timeout = %s)" % (self.callid, self.endpoint, self.args, self.sessionid, self.timeout)



class WampMessageCallResult(WampMessage):
   """
   A WAMP Call-Result message.
   """

   MESSAGE_TYPE = 64 + 4
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
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageEvent.MESSAGE_TYPE)

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

   
   def serialize(self, serializer):
      """
      Serialize this object into a wire level bytestring representation.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`
      """

      if self.result is not None:
         return serializer.serialize([WampMessageCallResult.MESSAGE_TYPE, self.callid, self.result])
      else:
         return serializer.serialize([WampMessageCallResult.MESSAGE_TYPE, self.callid])


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Call-Result Message (callid = '%s', result = %s)" % (self.callid, self.result)



class WampMessageCallError(WampMessage):
   """
   A WAMP Call-Error message.
   """

   MESSAGE_TYPE = 64 + 5
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, callid, error, message = None, value = None):
      """
      Message constructor.

      :param callid: The WAMP call ID of the original call this error is for.
      :type callid: str
      :param error: The WAMP or application error URI for the error that occured.
      :type error: str
      :param message: Human readable error message.
      :type message: str
      :param value: Arbitrary application error value to transport application error data for programatic consumption (must be serializable using the serializer in use).
      :type value: any
      """
      self.callid = callid
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
      assert(len(wmsg) > 0 and wmsg[0] == WampMessageEvent.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4):
         raise WampProtocolError("invalid message length %d for WAMP Call-Error message" % len(wmsg))

      ## callid
      ##
      if type(wmsg[1]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'callid' in WAMP Call-Error message" % type(wmsg[1]))

      callid = parse_wamp_callid(wmsg[1])
      if callid is None:
         raise WampProtocolError("invalid value '%s' for 'callid' in WAMP Call-Error message" % wmsg[1])

      ## error
      ##
      if type(wmsg[2]) not in (str, unicode):
         raise WampProtocolError("invalid type %s for 'callid' in WAMP Call-Error message" % type(wmsg[2]))

      error = parse_wamp_uri(wmsg[2])
      if error is None:
         raise WampProtocolError("invalid value '%s' for 'error' in WAMP Call-Error message" % wmsg[2])

      ## details
      ##
      message = None
      value = None

      if len(wmsg) == 4:
         details = wmsg[3]

         if type(details) != dict:
            raise WampProtocolError("invalid type %s for 'details' in WAMP Call-Error message" % type(options))

         for k in details.keys():
            if type(k) not in (str, unicode):
               raise WampProtocolError("invalid type %s for key in options in WAMP Call-Error message" % type(k))

         ## error message (should be human readable)
         ##
         if details.has_key('message'):

            option_message = options['message']
            if type(option_message) not in (str, unicode):
               raise WampProtocolError("invalid type %s for 'message' option in WAMP Call-Error message" % type(option_message))

            message = option_message

         ## arbitrary application error value
         ##
         value = details['value']

      obj = Klass(callid, error, message = message, value = value)

      return obj

   
   def serialize(self, serializer):
      """
      Serialize this object into a wire level bytestring representation.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`
      """
      details = {}

      if self.message is not None:
         details['message'] = self.message

      if self.value is not None:
         details['value'] = self.value

      if len(details):
         return serializer.serialize([WampMessageCallError.MESSAGE_TYPE, self.callid, self.error, details])
      else:
         return serializer.serialize([WampMessageCallError.MESSAGE_TYPE, self.callid, self.error])


   def __str__(self):
      """
      Returns text representation of this instance.

      :returns str -- Human readable representation (eg for logging or debugging purposes).
      """
      return "WAMP Call-Error Message (callid = '%s', error = '%s', message = '%s', value = %s)" % (self.callid, self.error, self.message, self.value)



class WampSerializer:
   """
   WAMP serializer is the core glue between parsed WAMP message objects and the
   bytes on wire (the transport).
   """

   MESSAGE_TYPE_MAP = {
      WampMessageSubscribe.MESSAGE_TYPE:     WampMessageSubscribe,
      WampMessageUnsubscribe.MESSAGE_TYPE:   WampMessageUnsubscribe,
      WampMessagePublish.MESSAGE_TYPE:       WampMessagePublish,
      WampMessageEvent.MESSAGE_TYPE:         WampMessageEvent,

      WampMessageCall.MESSAGE_TYPE:          WampMessageCall,
      WampMessageCallResult.MESSAGE_TYPE:    WampMessageCallResult,
      WampMessageCallError.MESSAGE_TYPE:     WampMessageCallError,
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
