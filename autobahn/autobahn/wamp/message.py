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

__all__ = ['Error',
           'Subscribe',
           'Subscribed',
           'Unsubscribe',
           'Unsubscribed',
           'Publish',
           'Published',
           'Event',
           'Register',
           'Registered',
           'Unregister',
           'Unregistered',
           'Call',
           'Cancel',
           'Result',
           'Invocation',
           'Interrupt',
           'Yield',
           'Hello',
           'Goodbye',
           'Heartbeat']


from zope.interface import implementer

from autobahn.wamp.exception import ProtocolError
from autobahn.wamp.interfaces import IMessage



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



class Message:
   """
   WAMP message base class. This is not supposed to be instantiated.
   """

   def __init__(self):
      """
      Base constructor.
      """
      self.reset_cache()


   def reset_cache(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.reset_cache`
      """
      ## serialization cache: mapping from ISerializer instances
      ## to serialized bytes
      ##
      self._serialized = {}


   def serialize(self, serializer):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.serialize`
      """
      ## only serialize if not cached ..
      if not self._serialized.has_key(serializer):
         self._serialized[serializer] = serializer.serialize(self.marshal())
      return self._serialized[serializer]


   def __eq__(self, other):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__eq__`
      """
      if not isinstance(other, self.__class__):
         return False
      # we only want the actual message data attributes (not eg _serialize)
      for k in self.__dict__:
         if not k.startswith('_'):
            if not self.__dict__[k] == other.__dict__[k]:
               return False
      return True
      #return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


   def __ne__(self, other):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__ne__`
      """
      return not self.__eq__(other)



@implementer(IMessage)
class Error(Message):
   """
   A WAMP `ERROR` message.

   Formats:
     * `[ERROR, REQUEST.Request|id, Details|dict, Error|uri]`
     * `[ERROR, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list]`
     * `[ERROR, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list, ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 4
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP Error Message (request = {}, error = {}, args = {}, kwargs = {})".format(self.request, self.error, self.args, self.kwargs)



@implementer(IMessage)
class Subscribe(Message):
   """
   A WAMP `SUBSCRIBE` message.

   Format: `[SUBSCRIBE, Request|id, Options|dict, Topic|uri]`
   """

   MESSAGE_TYPE = 32
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.match != Subscribe.MATCH_EXACT:
         options['match'] = self.match

      return [Subscribe.MESSAGE_TYPE, self.request, options, self.topic]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP SUBSCRIBE Message (request = {}, topic = {}, match = {})".format(self.request, self.topic, self.match)



@implementer(IMessage)
class Subscribed(Message):
   """
   A WAMP `SUBSCRIBED` message.

   Format: `[SUBSCRIBED, SUBSCRIBE.Request|id, Subscription|id]`
   """

   MESSAGE_TYPE = 33
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      return [Subscribed.MESSAGE_TYPE, self.request, self.subscription]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP SUBSCRIBED Message (request = {}, subscription = {})".format(self.request, self.subscription)



@implementer(IMessage)
class Unsubscribe(Message):
   """
   A WAMP `UNSUBSCRIBE` message.

   Format: `[UNSUBSCRIBE, Request|id, SUBSCRIBED.Subscription|id]`
   """

   MESSAGE_TYPE = 34
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      return [Unsubscribe.MESSAGE_TYPE, self.request, self.subscription]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP UNSUBSCRIBE Message (request = {}, subscription = {})".format(self.request, self.subscription)



@implementer(IMessage)
class Unsubscribed(Message):
   """
   A WAMP `UNSUBSCRIBED` message.

   Format: `[UNSUBSCRIBED, UNSUBSCRIBE.Request|id]`
   """

   MESSAGE_TYPE = 35
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      return [Unsubscribed.MESSAGE_TYPE, self.request]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP UNSUBSCRIBED Message (request = {})".format(self.request)



@implementer(IMessage)
class Publish(Message):
   """
   A WAMP `PUBLISH` message.

   Formats:
     * `[PUBLISH, Request|id, Options|dict, Topic|uri]`
     * `[PUBLISH, Request|id, Options|dict, Topic|uri, Arguments|list]`
     * `[PUBLISH, Request|id, Options|dict, Topic|uri, Arguments|list, ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 16
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request, topic, args = None, kwargs = None, excludeMe = None, exclude = None, eligible = None, discloseMe = None):
      """
      Message constructor.

      :param request: The WAMP request ID of this request.
      :type request: int
      :param topic: The WAMP or application URI of the PubSub topic the event should
                    be published to.
      :type topic: str
      :param args: Positional values for application-defined event payload.
                   Must be serializable using any serializers in use.
      :type args: list
      :param kwargs: Keyword values for application-defined event payload.
                     Must be serializable using any serializers in use.
      :type kwargs: dict
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP PUBLISH Message (request = {}, topic = {}, args = {}, kwargs = {}, excludeMe = {}, exclude = {}, eligible = {}, discloseMe = {})".format(self.request, self.topic, self.args, self.kwargs, self.excludeMe, self.exclude, self.eligible, self.discloseMe)



@implementer(IMessage)
class Published(Message):
   """
   A WAMP `PUBLISHED` message.

   Format: `[PUBLISHED, PUBLISH.Request|id, Publication|id]`
   """

   MESSAGE_TYPE = 17
   """
   The WAMP message code for this type of message.
   """

   def __init__(self, request, publication):
      """
      Message constructor.

      :param request: The request ID of the original `PUBLISH` request.
      :type request: int
      :param publication: The publication ID for the published event.
      :type publication: int
      """
      Message.__init__(self)
      self.request = request
      self.publication = publication


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
      assert(len(wmsg) > 0 and wmsg[0] == Published.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for PUBLISHED".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in PUBLISHED")
      publication = check_or_raise_id(wmsg[2], "'publication' in PUBLISHED")

      obj = Klass(request, publication)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      return [Published.MESSAGE_TYPE, self.request, self.publication]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP PUBLISHED Message (request = {}, publication = {})".format(self.request, self.publication)



@implementer(IMessage)
class Event(Message):
   """
   A WAMP `EVENT` message.

   Formats:

     * `[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict]`
     * `[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list]`
     * `[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list, PUBLISH.ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 36
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP EVENT Message (subscription = {}, publication = {}, args = {}, kwargs = {}, publisher = {})".format(self.subscription, self.publication, self.args, self.kwargs, self.publisher)



@implementer(IMessage)
class Register(Message):
   """
   A WAMP `REGISTER` message.

   Format: `[REGISTER, Request|id, Options|dict, Procedure|uri]`
   """

   MESSAGE_TYPE = 64
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.pkeys is not None:
         options['pkeys'] = self.pkeys

      return [Register.MESSAGE_TYPE, self.request, options, self.procedure]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP REGISTER Message (request = {}, procedure = {}, pkeys = {})".format(self.request, self.procedure, self.pkeys)



@implementer(IMessage)
class Registered(Message):
   """
   A WAMP `REGISTERED` message.

   Format: `[REGISTERED, REGISTER.Request|id, Registration|id]`
   """

   MESSAGE_TYPE = 65
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      return [Registered.MESSAGE_TYPE, self.request, self.registration]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP REGISTERED Message (request = {}, registration = {})".format(self.request, self.registration)



@implementer(IMessage)
class Unregister(Message):
   """
   A WAMP Unprovide message.

   Format: `[UNREGISTER, Request|id, REGISTERED.Registration|id]`
   """

   MESSAGE_TYPE = 66
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      return [Unregister.MESSAGE_TYPE, self.request, self.registration]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP UNREGISTER Message (request = {}, registration = {})".format(self.request, self.registration)



@implementer(IMessage)
class Unregistered(Message):
   """
   A WAMP `UNREGISTERED` message.

   Format: `[UNREGISTERED, UNREGISTER.Request|id]`
   """

   MESSAGE_TYPE = 67
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
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      return [Unregistered.MESSAGE_TYPE, self.request]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP UNREGISTER Message (request = {})".format(self.request)



@implementer(IMessage)
class Call(Message):
   """
   A WAMP `CALL` message.

   Formats:
     * `[CALL, Request|id, Options|dict, Procedure|uri]`
     * `[CALL, Request|id, Options|dict, Procedure|uri, Arguments|list]`
     * `[CALL, Request|id, Options|dict, Procedure|uri, Arguments|list, ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 48
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request, procedure, args = None, kwargs = None, timeout = None):
      """
      Message constructor.

      :param request: The WAMP request ID of this request.
      :type request: int
      :param topic: The WAMP or application URI of the procedure which should be called.
      :type topic: str
      :param args: Positional values for application-defined call arguments.
                   Must be serializable using any serializers in use.
      :type args: list
      :param kwargs: Keyword values for application-defined call arguments.
                     Must be serializable using any serializers in use.
      :param timeout: If present, let the callee automatically cancel
                      the call after this ms.
      :type timeout: int
      """
      Message.__init__(self)
      self.request = request
      self.procedure = procedure
      self.args = args
      self.kwargs = kwargs
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

      if len(wmsg) not in (4, 5, 6):
         raise ProtocolError("invalid message length {} for CALL".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in CALL")
      options = check_or_raise_dict(wmsg[2], "'options' in CALL")
      procedure = check_or_raise_uri(wmsg[3], "'procedure' in CALL")

      args = None
      if len(wmsg) > 4:
         args = wmsg[4]
         if type(args) != list:
            raise ProtocolError("invalid type {} for 'args' in CALL".format(type(args)))

      kwargs = None
      if len(wmsg) > 5:
         kwargs = wmsg[5]
         if type(kwargs) != dict:
            raise ProtocolError("invalid type {} for 'kwargs' in CALL".format(type(kwargs)))


      timeout = None

      if options.has_key('timeout'):

         option_timeout = options['timeout']
         if type(option_timeout) != int:
            raise ProtocolError("invalid type {} for 'timeout' option in CALL".format(type(option_timeout)))

         if option_timeout < 0:
            raise ProtocolError("invalid value {} for 'timeout' option in CALL".format(option_timeout))

         timeout = option_timeout

      obj = Klass(request, procedure, args = args, kwargs = kwargs, timeout = timeout)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.timeout is not None:
         options['timeout'] = self.timeout

      if self.kwargs:
         return [Call.MESSAGE_TYPE, self.request, options, self.procedure, self.args, self.kwargs]
      elif self.args:
         return [Call.MESSAGE_TYPE, self.request, options, self.procedure, self.args]
      else:
         return [Call.MESSAGE_TYPE, self.request, options, self.procedure]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP CALL Message (request = {}, procedure = {}, args = {}, kwargs = {}, timeout = {})" % (self.request, self.procedure, self.args, self.kwargs, self.timeout)



@implementer(IMessage)
class Cancel(Message):
   """
   A WAMP `CANCEL` message.

   Format: `[CANCEL, CALL.Request|id, Options|dict]`
   """

   MESSAGE_TYPE = 49
   """
   The WAMP message code for this type of message.
   """

   SKIP = 'skip'
   ABORT = 'abort'
   KILL = 'kill'


   def __init__(self, request, mode = None):
      """
      Message constructor.

      :param request: The WAMP request ID of the original `CALL` to cancel.
      :type request: int
      :param mode: Specifies how to cancel the call (skip, abort or kill).
      :type mode: str
      """
      Message.__init__(self)
      self.request = request
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
      assert(len(wmsg) > 0 and wmsg[0] == Cancel.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for CANCEL".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in CANCEL")
      options = check_or_raise_dict(wmsg[2], "'options' in CANCEL")

      ## options
      ##
      mode = None

      if options.has_key('mode'):

         option_mode = options['mode']
         if type(option_mode) not in (str, unicode):
            raise ProtocolError("invalid type {} for 'mode' option in CANCEL".format(type(option_mode)))

         if option_mode not in [Cancel.SKIP, Cancel.ABORT, Cancel.KILL]:
            raise ProtocolError("invalid value '{}' for 'mode' option in CANCEL".format(option_mode))

         mode = option_mode

      obj = Klass(request, mode = mode)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.mode is not None:
         options['mode'] = self.mode

      return [Cancel.MESSAGE_TYPE, self.request, options]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP CANCEL Message (request = {}, mode = '{}'')" % (self.request, self.mode)



@implementer(IMessage)
class Result(Message):
   """
   A WAMP `RESULT` message.

   Formats:
     * `[RESULT, CALL.Request|id, Details|dict]`
     * `[RESULT, CALL.Request|id, Details|dict, YIELD.Arguments|list]`
     * `[RESULT, CALL.Request|id, Details|dict, YIELD.Arguments|list, YIELD.ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 50
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request, args = None, kwargs = None, progress = None):
      """
      Message constructor.

      :param request: The request ID of the original `CALL` request.
      :type request: int
      :param args: Positional values for application-defined event payload.
                   Must be serializable using any serializers in use.
      :type args: list
      :param kwargs: Keyword values for application-defined event payload.
                     Must be serializable using any serializers in use.
      :type kwargs: dict
      :progress: If `True`, this result is a progressive call result, and subsequent
                 results (or a final error) will follow.
      """
      assert(not (kwargs and not args))
      Message.__init__(self)
      self.request = request
      self.args = args
      self.kwargs = kwargs
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
      assert(len(wmsg) > 0 and wmsg[0] == Result.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4, 5):
         raise ProtocolError("invalid message length {} for RESULT".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in RESULT")
      details = check_or_raise_dict(wmsg[2], "'details' in RESULT")

      args = None
      if len(wmsg) > 3:
         args = wmsg[3]
         if type(args) != list:
            raise ProtocolError("invalid type {} for 'args' in RESULT".format(type(args)))

      kwargs = None
      if len(wmsg) > 4:
         kwargs = wmsg[4]
         if type(kwargs) != dict:
            raise ProtocolError("invalid type {} for 'kwargs' in RESULT".format(type(kwargs)))

      progress = None

      if details.has_key('progress'):

         detail_progress = details['progress']
         if type(detail_progress) != bool:
            raise ProtocolError("invalid type {} for 'progress' option in RESULT".format(type(detail_progress)))

         progress = detail_progress

      obj = Klass(request, args = args, kwargs = kwargs, progress = progress)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      details = {}

      if self.progress is not None:
         details['progress'] = self.progress

      if self.kwargs:
         return [Result.MESSAGE_TYPE, self.request, details, self.args, self.kwargs]
      elif self.args:
         return [Result.MESSAGE_TYPE, self.request, details, self.args]
      else:
         return [Result.MESSAGE_TYPE, self.request, details]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP RESULT Message (request = {}, args = {}, kwargs = {}, progress = {})" % (self.request, self.args, self.kwargs, self.progress)



@implementer(IMessage)
class Invocation(Message):
   """
   A WAMP `INVOCATION` message.

   Formats:
     * `[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict]`
     * `[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, Arguments|list]`
     * `[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, Arguments|list, ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 68
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request, registration, args = None, kwargs = None, timeout = None):
      """
      Message constructor.

      :param request: The WAMP request ID of this request.
      :type request: int
      :param registration: The registration ID of the endpoint to be invoked.
      :type registration: int
      :param args: Positional values for application-defined event payload.
                   Must be serializable using any serializers in use.
      :type args: list
      :param kwargs: Keyword values for application-defined event payload.
                     Must be serializable using any serializers in use.
      :type kwargs: dict
      :param timeout: If present, let the callee automatically cancels
                      the invocation after this ms.
      :type timeout: int
      """
      Message.__init__(self)
      self.request = request
      self.registration = registration
      self.args = args
      self.kwargs = kwargs
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
      assert(len(wmsg) > 0 and wmsg[0] == Invocation.MESSAGE_TYPE)

      if len(wmsg) not in (4, 5, 6):
         raise ProtocolError("invalid message length {} for INVOCATION".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in INVOCATION")
      registration = check_or_raise_id(wmsg[2], "'registration' in INVOCATION")
      details = check_or_raise_dict(wmsg[3], "'details' in INVOCATION")

      args = None
      if len(wmsg) > 4:
         args = wmsg[4]
         if type(args) != list:
            raise ProtocolError("invalid type {} for 'args' in INVOCATION".format(type(args)))

      kwargs = None
      if len(wmsg) > 5:
         kwargs = wmsg[5]
         if type(kwargs) != dict:
            raise ProtocolError("invalid type {} for 'kwargs' in INVOCATION".format(type(kwargs)))


      timeout = None

      if details.has_key('timeout'):

         detail_timeout = details['timeout']
         if type(detail_timeout) != int:
            raise ProtocolError("invalid type {} for 'timeout' detail in INVOCATION".format(type(detail_timeout)))

         if detail_timeout < 0:
            raise ProtocolError("invalid value {} for 'timeout' detail in INVOCATION".format(detail_timeout))

         timeout = detail_timeout

      obj = Klass(request, registration, args = args, kwargs = kwargs, timeout = timeout)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.timeout is not None:
         options['timeout'] = self.timeout

      if self.kwargs:
         return [Invocation.MESSAGE_TYPE, self.request, self.registration, options, self.args, self.kwargs]
      elif self.args:
         return [Invocation.MESSAGE_TYPE, self.request, self.registration, options, self.args]
      else:
         return [Invocation.MESSAGE_TYPE, self.request, self.registration, options]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP INVOCATION Message (request = {}, registration = {}, args = {}, kwargs = {}, timeout = {})" % (self.request, self.registration, self.args, self.kwargs, self.timeout)



@implementer(IMessage)
class Interrupt(Message):
   """
   A WAMP `INTERRUPT` message.

   Format: `[INTERRUPT, INVOCATION.Request|id, Options|dict]`
   """

   MESSAGE_TYPE = 69
   """
   The WAMP message code for this type of message.
   """

   ABORT = 'abort'
   KILL = 'kill'


   def __init__(self, request, mode = None):
      """
      Message constructor.

      :param request: The WAMP request ID of the original `INVOCATION` to interrupt.
      :type request: int
      :param mode: Specifies how to interrupt the invocation (abort or kill).
      :type mode: str
      """
      Message.__init__(self)
      self.request = request
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
      assert(len(wmsg) > 0 and wmsg[0] == Interrupt.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for INTERRUPT".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in INTERRUPT")
      options = check_or_raise_dict(wmsg[2], "'options' in INTERRUPT")

      ## options
      ##
      mode = None

      if options.has_key('mode'):

         option_mode = options['mode']
         if type(option_mode) not in (str, unicode):
            raise ProtocolError("invalid type {} for 'mode' option in INTERRUPT".format(type(option_mode)))

         if option_mode not in [Interrupt.ABORT, Interrupt.KILL]:
            raise ProtocolError("invalid value '{}' for 'mode' option in INTERRUPT".format(option_mode))

         mode = option_mode

      obj = Klass(request, mode = mode)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.mode is not None:
         options['mode'] = self.mode

      return [Interrupt.MESSAGE_TYPE, self.request, options]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP INTERRUPT Message (request = {}, mode = '{}'')" % (self.request, self.mode)



@implementer(IMessage)
class Yield(Message):
   """
   A WAMP `YIELD` message.

   Formats:
     * `[YIELD, Request|id, Options|dict]`
     * `[YIELD, Request|id, Options|dict, Arguments|list]`
     * `[YIELD, Request|id, Options|dict, Arguments|list, ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 70
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request, args = None, kwargs = None, progress = None):
      """
      Message constructor.

      :param request: The WAMP request ID of this request.
      :type request: int
      :param args: Positional values for application-defined event payload.
                   Must be serializable using any serializers in use.
      :type args: list
      :param kwargs: Keyword values for application-defined event payload.
                     Must be serializable using any serializers in use.
      :type kwargs: dict
      :progress: If `True`, this result is a progressive invocation result, and subsequent
                 results (or a final error) will follow.
      """
      Message.__init__(self)
      self.request = request
      self.args = args
      self.kwargs = kwargs
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
      assert(len(wmsg) > 0 and wmsg[0] == Yield.MESSAGE_TYPE)

      if len(wmsg) not in (3, 4, 5):
         raise ProtocolError("invalid message length {} for YIELD".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in YIELD")
      options = check_or_raise_dict(wmsg[2], "'options' in YIELD")

      args = None
      if len(wmsg) > 3:
         args = wmsg[3]
         if type(args) != list:
            raise ProtocolError("invalid type {} for 'args' in YIELD".format(type(args)))

      kwargs = None
      if len(wmsg) > 4:
         kwargs = wmsg[4]
         if type(kwargs) != dict:
            raise ProtocolError("invalid type {} for 'kwargs' in YIELD".format(type(kwargs)))

      progress = None

      if options.has_key('progress'):

         option_progress = options['progress']
         if type(option_progress) != bool:
            raise ProtocolError("invalid type {} for 'progress' option in YIELD".format(type(option_progress)))

         progress = option_progress

      obj = Klass(request, args = args, kwargs = kwargs, progress = progress)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.progress is not None:
         options['progress'] = self.progress

      if self.kwargs:
         return [Yield.MESSAGE_TYPE, self.request, options, self.args, self.kwargs]
      elif self.args:
         return [Yield.MESSAGE_TYPE, self.request, options, self.args]
      else:
         return [Yield.MESSAGE_TYPE, self.request, options]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP YIELD Message (request = {}, args = {}, kwargs = {}, progress = {})" % (self.request, self.args, self.kwargs, self.progress)



@implementer(IMessage)
class Hello(Message):
   """
   A WAMP `HELLO` message.

   Format: `[HELLO, Session|id, Details|dict]`
   """

   MESSAGE_TYPE = 1
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, session):
      """
      Message constructor.

      :param session: The WAMP session ID the other peer is assigned.
      :type session: int
      """
      Message.__init__(self)
      self.session = session


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

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for HELLO".format(len(wmsg)))

      session = check_or_raise_id(wmsg[1], "'session' in HELLO")
      details = check_or_raise_dict(wmsg[2], "'details' in HELLO")

      obj = Klass(session)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      details = {}
      return [Hello.MESSAGE_TYPE, self.session, details]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP HELLO Message (session = '%s')" % (self.session)



@implementer(IMessage)
class Goodbye(Message):
   """
   A WAMP `GOODBYE` message.

   Format: `[GOODBYE, Details|dict]`
   """

   MESSAGE_TYPE = 2
   """
   The WAMP message code for this type of message.
   """


   def __init__(self):
      """
      Message constructor.
      """
      Message.__init__(self)


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
      assert(len(wmsg) > 0 and wmsg[0] == Goodbye.MESSAGE_TYPE)

      if len(wmsg) != 2:
         raise ProtocolError("invalid message length {} for GOODBYE".format(len(wmsg)))

      details = check_or_raise_dict(wmsg[1], "'details' in GOODBYE")

      obj = Klass()

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      details = {}
      return [Goodbye.MESSAGE_TYPE, details]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP GOODBYE Message ()"



@implementer(IMessage)
class Heartbeat(Message):
   """
   A WAMP `HEARTBEAT` message.

   Formats:

     * `[HEARTBEAT, Incoming|integer, Outgoing|integer]`
     * `[HEARTBEAT, Incoming|integer, Outgoing|integer, Discard|string]`
   """

   MESSAGE_TYPE = 3
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, incoming, outgoing, discard = None):
      """
      Message constructor.

      :param incoming: Last incoming heartbeat processed from peer.
      :type incoming: int
      :param outgoing: Outgoing heartbeat.
      :type outgoing: int
      :param discard: Optional data that is discared by peer.
      :type discard: str
      """
      Message.__init__(self)
      self.incoming = incoming
      self.outgoing = outgoing
      self.discard = discard


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

      if len(wmsg) not in [3, 4]:
         raise ProtocolError("invalid message length {} for HEARTBEAT".format(len(wmsg)))

      incoming = wmsg[1]

      if type(incoming) != int:
         raise ProtocolError("invalid type {} for 'incoming' in HEARTBEAT".format(type(incoming)))

      if incoming < 0: # must be non-negative
         raise ProtocolError("invalid value {} for 'incoming' in HEARTBEAT".format(incoming))

      outgoing = wmsg[2]

      if type(outgoing) != int:
         raise ProtocolError("invalid type %s for 'outgoing' in HEARTBEAT".format(type(outgoing)))

      if outgoing <= 0: # must be positive
         raise ProtocolError("invalid value %d for 'outgoing' in HEARTBEAT".format(outgoing))

      discard = None
      if len(wmsg) > 3:
         discard = wmsg[3]
         if type(discard) not in (str, unicode):
            raise ProtocolError("invalid type {} for 'discard' in HEARTBEAT".format(type(discard)))

      obj = Klass(incoming, outgoing, discard = discard)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      if self.discard:
         return [Heartbeat.MESSAGE_TYPE, self.incoming, self.outgoing, self.discard]
      else:
         return [Heartbeat.MESSAGE_TYPE, self.incoming, self.outgoing]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP HEARTBEAT Message (incoming {}, outgoing = {}, len(discard) = {})" % (self.incoming, self.outgoing, len(self.discard) if self.discard else None)




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
