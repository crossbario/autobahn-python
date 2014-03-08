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

__all__ = ['Hello',
           'Welcome',
           'Abort',
           'Challenge',
           'Authenticate',
           'Goodbye',
           'Heartbeat'
           'Error',
           'Publish',
           'Published',          
           'Subscribe',
           'Subscribed',
           'Unsubscribe',
           'Unsubscribed',
           'Event',
           'Call',
           'Cancel',
           'Result',
           'Register',
           'Registered',
           'Unregister',
           'Unregistered',
           'Invocation',
           'Interrupt',
           'Yield']


import re

from zope.interface import implementer

import autobahn
from autobahn import util
from autobahn.wamp.exception import ProtocolError
from autobahn.wamp.interfaces import IMessage


## strict URI check
_URI_PAT_STRICT = re.compile(r"^(([0-9a-z_]{2,}\.)|\.)*([0-9a-z_]{2,})?$")

## loose URI check
_URI_PAT_LOOSE = re.compile(r"^(([^\s\.#]+\.)|\.)*([^\s\.#]+)?$")




def check_or_raise_uri(value, message):
   if type(value) not in [str, unicode]:
      raise ProtocolError("{}: invalid type {} for URI".format(message, type(value)))
   if not _URI_PAT_LOOSE.match(value):
      raise ProtocolError("{}: invalid value '{}' for URI".format(message, value))
   return value



def check_or_raise_id(value, message):
   if type(value) not in [int, long]:
      raise ProtocolError("{}: invalid type {} for ID".format(message, type(value)))
   if value < 0 or value > 9007199254740992: # 2**53
      raise ProtocolError("{}: invalid value {} for ID".format(message, value))
   return value



def check_or_raise_extra(value, message):
   if type(value) != dict:
      raise ProtocolError("{}: invalid type {}".format(message, type(value)))
   for k in value.keys():
      if type(k) not in (str, unicode):
         raise ProtocolError("{}: invalid type {} for key '{}'".format(type(k), k))
   return value



class Message(util.EqualityMixin):
   """
   WAMP message base class. This is not supposed to be instantiated.
   """

   def __init__(self):
      """
      Base constructor.
      """
      ## serialization cache: mapping from ISerializer instances
      ## to serialized bytes
      ##
      self._serialized = {}


   def uncache(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.uncache`
      """
      self._serialized = {}


   def serialize(self, serializer):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.serialize`
      """
      ## only serialize if not cached ..
      if not self._serialized.has_key(serializer):
         self._serialized[serializer] = serializer.serialize(self.marshal())
      return self._serialized[serializer]



@implementer(IMessage)
class Hello(Message):
   """
   A WAMP `HELLO` message.

   Format: `[HELLO, Realm|uri, Details|dict]`
   """

   MESSAGE_TYPE = 1
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, realm, roles, authmethods = None):
      """
      Message constructor.

      :param realm: The URI of the WAMP realm to join.
      :type realm: str
      :param roles: The WAMP roles to announce.
      :type roles: list of :class:`autobahn.wamp.role.RoleFeatures`
      """
      for role in roles:
         assert(isinstance(role, autobahn.wamp.role.RoleFeatures))
      Message.__init__(self)
      self.realm = realm
      self.roles = roles
      self.authmethods = authmethods


   @staticmethod
   def parse(wmsg):
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

      realm = check_or_raise_uri(wmsg[1], "'realm' in HELLO")
      details = check_or_raise_extra(wmsg[2], "'details' in HELLO")

      roles = []

      if not details.has_key('roles'):
         raise ProtocolError("missing mandatory roles attribute in options in HELLO")

      details_roles = check_or_raise_extra(details['roles'], "'roles' in 'details' in HELLO")

      if len(details_roles) == 0:
         raise ProtocolError("empty 'roles' in 'details' in HELLO")

      for role in details_roles:
         if role not in autobahn.wamp.role.ROLE_NAME_TO_CLASS:
            raise ProtocolError("invalid role '{}' in 'roles' in 'details' in HELLO".format(role))

         if details_roles[role].has_key('features'):
            details_role_features = check_or_raise_extra(details_roles[role]['features'], "'features' in role '{}' in 'roles' in 'details' in HELLO".format(role))

            ## FIXME: skip unknown attributes
            role_features = autobahn.wamp.role.ROLE_NAME_TO_CLASS[role](**details_roles[role]['features'])

         else:
            role_features = autobahn.wamp.role.ROLE_NAME_TO_CLASS[role]()

         roles.append(role_features)

      authmethods = None
      if 'authmethods' in details:
         details_authmethods = details['authmethods']
         if type(details_authmethods) != list:
            raise ProtocolError("invalid type {} for 'authmethods' detail in HELLO".format(type(details_authmethods)))

         for auth_method in details_authmethods:
            if type(auth_method) not in [str, unicode]:
               raise ProtocolError("invalid type {} for item in 'authmethods' detail in HELLO".format(type(auth_method)))

         authmethods = details_authmethods

      obj = Hello(realm, roles, authmethods)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      details = {'roles': {}}
      for role in self.roles:
         details['roles'][role.ROLE] = {}
         for feature in role.__dict__:
            if not feature.startswith('_') and feature != 'ROLE' and getattr(role, feature) is not None:
               if not details['roles'][role.ROLE].has_key('features'):
                  details['roles'][role.ROLE] = {'features': {}}
               details['roles'][role.ROLE]['features'][feature] = getattr(role, feature)

      if self.authmethods:
         details['authmethods'] = self.authmethods

      return [Hello.MESSAGE_TYPE, self.realm, details]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP HELLO Message (realm = {}, roles = {}, authmethods = {})".format(self.realm, self.roles, self.authmethods)



@implementer(IMessage)
class Welcome(Message):
   """
   A WAMP `WELCOME` message.

   Format: `[WELCOME, Session|id, Details|dict]`
   """

   MESSAGE_TYPE = 2
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, session, roles, authid = None, authrole = None, authmethod = None):
      """
      Message constructor.

      :param session: The WAMP session ID the other peer is assigned.
      :type session: int
      """
      for role in roles:
         assert(isinstance(role, autobahn.wamp.role.RoleFeatures))
      Message.__init__(self)
      self.session = session
      self.roles = roles
      self.authid = authid
      self.authrole = authrole
      self.authmethod = authmethod


   @staticmethod
   def parse(wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == Welcome.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for WELCOME".format(len(wmsg)))

      session = check_or_raise_id(wmsg[1], "'session' in WELCOME")
      details = check_or_raise_extra(wmsg[2], "'details' in WELCOME")

      authid = details.get('authid', None)
      authrole = details.get('authrole', None)
      authmethod = details.get('authmethod', None)

      roles = []

      if not details.has_key('roles'):
         raise ProtocolError("missing mandatory roles attribute in options in WELCOME")

      details_roles = check_or_raise_extra(details['roles'], "'roles' in 'details' in WELCOME")

      if len(details_roles) == 0:
         raise ProtocolError("empty 'roles' in 'details' in WELCOME")

      for role in details_roles:
         if role not in autobahn.wamp.role.ROLE_NAME_TO_CLASS:
            raise ProtocolError("invalid role '{}' in 'roles' in 'details' in WELCOME".format(role))

         if details_roles[role].has_key('features'):
            details_role_features = check_or_raise_extra(details_roles[role]['features'], "'features' in role '{}' in 'roles' in 'details' in WELCOME".format(role))

            ## FIXME: skip unknown attributes
            role_features = autobahn.wamp.role.ROLE_NAME_TO_CLASS[role](**details_roles[role]['features'])

         else:
            role_features = autobahn.wamp.role.ROLE_NAME_TO_CLASS[role]()

         roles.append(role_features)

      obj = Welcome(session, roles, authid, authrole, authmethod)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      details = {
         'roles': {}
      }

      if self.authid:
         details['authid'] = self.authid

      if self.authrole:
         details['authrole'] = self.authrole

      if self.authrole:
         details['authmethod'] = self.authmethod

      for role in self.roles:
         details['roles'][role.ROLE] = {}
         for feature in role.__dict__:
            if not feature.startswith('_') and feature != 'ROLE' and getattr(role, feature) is not None:
               if not details['roles'][role.ROLE].has_key('features'):
                  details['roles'][role.ROLE] = {'features': {}}
               details['roles'][role.ROLE]['features'][feature] = getattr(role, feature)

      return [Welcome.MESSAGE_TYPE, self.session, details]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP WELCOME Message (session = {}, roles = {}, authid = {}, authrole = {}, authmethod = {})".format(self.session, self.roles, self.authid, self.authrole, self.authmethod)



@implementer(IMessage)
class Abort(Message):
   """
   A WAMP `ABORT` message.

   Format: `[ABORT, Details|dict, Reason|uri]`
   """

   MESSAGE_TYPE = 3
   """
   The WAMP message code for this type of message.
   """

   def __init__(self, reason, message = None):
      """
      Message constructor.

      :param reason: WAMP or application error URI for aborting reason.
      :type reason: str
      :param message: Optional human-readable closing message, e.g. for logging purposes.
      :type message: str
      """
      Message.__init__(self)
      self.reason = reason
      self.message = message


   @staticmethod
   def parse(wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == Abort.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for ABORT".format(len(wmsg)))

      details = check_or_raise_extra(wmsg[1], "'details' in ABORT")
      reason = check_or_raise_uri(wmsg[2], "'reason' in ABORT")

      message = None

      if details.has_key('message'):

         details_message = details['message']
         if type(details_message) not in [str, unicode]:
            raise ProtocolError("invalid type {} for 'message' detail in ABORT".format(type(details_message)))

         message = details_message

      obj = Abort(reason, message)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      details = {}
      if self.message:
         details['message'] = self.message

      return [Abort.MESSAGE_TYPE, details, self.reason]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP ABORT Message (message = {}, reason = {})".format(self.message, self.reason)



@implementer(IMessage)
class Challenge(Message):
   """
   A WAMP `CHALLENGE` message.

   Format: `[CHALLENGE, Method|string, Extra|dict]`
   """

   MESSAGE_TYPE = 4
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, method, extra = {}):
      """
      Message constructor.

      :param method: The authentication method.
      :type method: str
      :param extra: Authentication method specific information.
      :type extra: dict
      """
      Message.__init__(self)
      self.method = method
      self.extra = extra


   @staticmethod
   def parse(wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == Challenge.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for CHALLENGE".format(len(wmsg)))

      method = wmsg[1]
      if type(method) != str:
         raise ProtocolError("invalid type {} for 'method' in CHALLENGE".format(type(method)))

      extra = check_or_raise_extra(wmsg[2], "'extra' in CHALLENGE")

      obj = Challenge(method, extra)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      return [Challenge.MESSAGE_TYPE, self.method, self.extra or {}]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP CHALLENGE Message (method = {}, extra = {})".format(self.method, self.extra)



@implementer(IMessage)
class Authenticate(Message):
   """
   A WAMP `AUTHENTICATE` message.

   Format: `[AUTHENTICATE, Signature|string, Extra|dict]`
   """

   MESSAGE_TYPE = 5
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, signature):
      """
      Message constructor.

      :param signature: The signature for the authentication challenge.
      :type signature: str
      """
      Message.__init__(self)
      self.signature = signature


   @staticmethod
   def parse(wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == Authenticate.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for AUTHENTICATE".format(len(wmsg)))

      signature = wmsg[1]
      if type(signature) not in [str, unicode]:
         raise ProtocolError("invalid type {} for 'signature' in AUTHENTICATE".format(type(signature)))

      extra = check_or_raise_extra(wmsg[2], "'extra' in AUTHENTICATE")

      obj = Authenticate(signature)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      extra = {}
      return [Authenticate.MESSAGE_TYPE, self.signature, extra]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP AUTHENTICATE Message (signature = {})".format(self.signature)



@implementer(IMessage)
class Goodbye(Message):
   """
   A WAMP `GOODBYE` message.

   Format: `[GOODBYE, Details|dict, Reason|uri]`
   """

   MESSAGE_TYPE = 6
   """
   The WAMP message code for this type of message.
   """

   DEFAULT_REASON = "wamp.goodbye.normal"
   """
   Default WAMP closing reason.
   """


   def __init__(self, reason = DEFAULT_REASON, message = None):
      """
      Message constructor.

      :param reason: Optional WAMP or application error URI for closing reason.
      :type reason: str
      :param message: Optional human-readable closing message, e.g. for logging purposes.
      :type message: str
      """
      Message.__init__(self)
      self.reason = reason
      self.message = message


   @staticmethod
   def parse(wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == Goodbye.MESSAGE_TYPE)

      if len(wmsg) != 3:
         raise ProtocolError("invalid message length {} for GOODBYE".format(len(wmsg)))

      details = check_or_raise_extra(wmsg[1], "'details' in GOODBYE")
      reason = check_or_raise_uri(wmsg[2], "'reason' in GOODBYE")

      message = None

      if details.has_key('message'):

         details_message = details['message']
         if type(details_message) not in [str, unicode]:
            raise ProtocolError("invalid type {} for 'message' detail in GOODBYE".format(type(details_message)))

         message = details_message

      obj = Goodbye(reason, message)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      details = {}
      if self.message:
         details['message'] = self.message

      return [Goodbye.MESSAGE_TYPE, details, self.reason]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP GOODBYE Message (message = {}, reason = {})".format(self.message, self.reason)



@implementer(IMessage)
class Heartbeat(Message):
   """
   A WAMP `HEARTBEAT` message.

   Formats:

     * `[HEARTBEAT, Incoming|integer, Outgoing|integer]`
     * `[HEARTBEAT, Incoming|integer, Outgoing|integer, Discard|string]`
   """

   MESSAGE_TYPE = 7
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


   @staticmethod
   def parse(wmsg):
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

      if type(incoming) not in [int, long]:
         raise ProtocolError("invalid type {} for 'incoming' in HEARTBEAT".format(type(incoming)))

      if incoming < 0: # must be non-negative
         raise ProtocolError("invalid value {} for 'incoming' in HEARTBEAT".format(incoming))

      outgoing = wmsg[2]

      if type(outgoing) not in [int, long]:
         raise ProtocolError("invalid type {} for 'outgoing' in HEARTBEAT".format(type(outgoing)))

      if outgoing <= 0: # must be positive
         raise ProtocolError("invalid value {} for 'outgoing' in HEARTBEAT".format(outgoing))

      discard = None
      if len(wmsg) > 3:
         discard = wmsg[3]
         if type(discard) not in (str, unicode):
            raise ProtocolError("invalid type {} for 'discard' in HEARTBEAT".format(type(discard)))

      obj = Heartbeat(incoming, outgoing, discard = discard)

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
      return "WAMP HEARTBEAT Message (incoming {}, outgoing = {}, len(discard) = {})".format(self.incoming, self.outgoing, len(self.discard) if self.discard else None)



@implementer(IMessage)
class Error(Message):
   """
   A WAMP `ERROR` message.

   Formats:
     * `[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri]`
     * `[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list]`
     * `[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list, ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 8
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request_type, request, error, args = None, kwargs = None):
      """
      Message constructor.

      :param request_type: The WAMP message type code for the original request.
      :type request_type: int
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
      Message.__init__(self)
      self.request_type = request_type
      self.request = request
      self.error = error
      self.args = args
      self.kwargs = kwargs


   @staticmethod
   def parse(wmsg):
      """
      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns obj -- An instance of this class.
      """
      ## this should already be verified by WampSerializer.unserialize
      ##
      assert(len(wmsg) > 0 and wmsg[0] == Error.MESSAGE_TYPE)

      if len(wmsg) not in (5, 6, 7):
         raise ProtocolError("invalid message length {} for ERROR".format(len(wmsg)))

      request_type = wmsg[1]
      if type(request_type) not in [int, long]:
         raise ProtocolError("invalid type {} for 'request_type' in ERROR".format(request_type))

      if request_type not in [Subscribe.MESSAGE_TYPE,
                              Unsubscribe.MESSAGE_TYPE,
                              Publish.MESSAGE_TYPE,
                              Register.MESSAGE_TYPE,
                              Unregister.MESSAGE_TYPE,
                              Call.MESSAGE_TYPE,
                              Invocation.MESSAGE_TYPE]:
         raise ProtocolError("invalid value {} for 'request_type' in ERROR".format(request_type))

      request = check_or_raise_id(wmsg[2], "'request' in ERROR")
      details = check_or_raise_extra(wmsg[3], "'details' in ERROR")
      error = check_or_raise_uri(wmsg[4], "'error' in ERROR")

      args = None
      if len(wmsg) > 5:
         args = wmsg[5]
         if type(args) != list:
            raise ProtocolError("invalid type {} for 'args' in ERROR".format(type(args)))

      kwargs = None
      if len(wmsg) > 6:
         kwargs = wmsg[6]
         if type(kwargs) != dict:
            raise ProtocolError("invalid type {} for 'kwargs' in ERROR".format(type(kwargs)))

      obj = Error(request_type, request, error, args = args, kwargs = kwargs)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      details = {}

      if self.kwargs:
         return [self.MESSAGE_TYPE, self.request_type, self.request, details, self.error, self.args, self.kwargs]
      elif self.args:
         return [self.MESSAGE_TYPE, self.request_type, self.request, details, self.error, self.args]
      else:
         return [self.MESSAGE_TYPE, self.request_type, self.request, details, self.error]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP Error Message (request_type = {}, request = {}, error = {}, args = {}, kwargs = {})".format(self.request_type, self.request, self.error, self.args, self.kwargs)



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

   def __init__(self,
                request,
                topic,
                args = None,
                kwargs = None,
                acknowledge = None,
                excludeMe = None,
                exclude = None,
                eligible = None,
                discloseMe = None):
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
      :param acknowledge: If True, acknowledge the publication with a success or
                          error response.
      :type acknowledge: bool
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
      Message.__init__(self)
      self.request = request
      self.topic = topic
      self.args = args
      self.kwargs = kwargs
      self.acknowledge = acknowledge
      self.excludeMe = excludeMe
      self.exclude = exclude
      self.eligible = eligible
      self.discloseMe = discloseMe


   @staticmethod
   def parse(wmsg):
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
      options = check_or_raise_extra(wmsg[2], "'options' in PUBLISH")
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

      acknowledge = None
      excludeMe = None
      exclude = None
      eligible = None
      discloseMe = None

      if options.has_key('acknowledge'):

         option_acknowledge = options['acknowledge']
         if type(option_acknowledge) != bool:
            raise ProtocolError("invalid type {} for 'acknowledge' option in PUBLISH".format(type(option_acknowledge)))

         acknowledge = option_acknowledge

      if options.has_key('exclude_me'):

         option_excludeMe = options['exclude_me']
         if type(option_excludeMe) != bool:
            raise ProtocolError("invalid type {} for 'exclude_me' option in PUBLISH".format(type(option_excludeMe)))

         excludeMe = option_excludeMe

      if options.has_key('exclude'):

         option_exclude = options['exclude']
         if type(option_exclude) != list:
            raise ProtocolError("invalid type {} for 'exclude' option in PUBLISH".format(type(option_exclude)))

         for sessionId in option_exclude:
            if type(sessionId) not in [int, long]:
               raise ProtocolError("invalid type {} for value in 'exclude' option in PUBLISH".format(type(sessionId)))

         exclude = option_exclude

      if options.has_key('eligible'):

         option_eligible = options['eligible']
         if type(option_eligible) != list:
            raise ProtocolError("invalid type {} for 'eligible' option in PUBLISH".format(type(option_eligible)))

         for sessionId in option_eligible:
            if type(sessionId) not in [int, long]:
               raise ProtocolError("invalid type {} for value in 'eligible' option in PUBLISH".format(type(sessionId)))

         eligible = option_eligible

      if options.has_key('disclose_me'):

         option_discloseMe = options['disclose_me']
         if type(option_discloseMe) != bool:
            raise ProtocolError("invalid type {} for 'disclose_me' option in PUBLISH".format(type(option_discloseMe)))

         discloseMe = option_discloseMe

      obj = Publish(request,
                    topic,
                    args = args,
                    kwargs = kwargs,
                    acknowledge = acknowledge,
                    excludeMe = excludeMe,
                    exclude = exclude,
                    eligible = eligible,
                    discloseMe = discloseMe)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.acknowledge is not None:
         options['acknowledge'] = self.acknowledge
      if self.excludeMe is not None:
         options['exclude_me'] = self.excludeMe
      if self.exclude is not None:
         options['exclude'] = self.exclude
      if self.eligible is not None:
         options['eligible'] = self.eligible
      if self.discloseMe is not None:
         options['disclose_me'] = self.discloseMe

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
      return "WAMP PUBLISH Message (request = {}, topic = {}, args = {}, kwargs = {}, acknowledge = {}, excludeMe = {}, exclude = {}, eligible = {}, discloseMe = {})".format(self.request, self.topic, self.args, self.kwargs, self.acknowledge, self.excludeMe, self.exclude, self.eligible, self.discloseMe)



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


   @staticmethod
   def parse(wmsg):
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

      obj = Published(request, publication)

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
      :type match: str
      """
      Message.__init__(self)
      self.request = request
      self.topic = topic
      self.match = match


   @staticmethod
   def parse(wmsg):
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
         raise ProtocolError("invalid message length {} for SUBSCRIBE".format(len(wmsg)))

      request = check_or_raise_id(wmsg[1], "'request' in SUBSCRIBE")
      options = check_or_raise_extra(wmsg[2], "'options' in SUBSCRIBE")
      topic = check_or_raise_uri(wmsg[3], "'topic' in SUBSCRIBE")

      match = Subscribe.MATCH_EXACT

      if options.has_key('match'):

         option_match = options['match']
         if type(option_match) not in [str, unicode]:
            raise ProtocolError("invalid type {} for 'match' option in SUBSCRIBE".format(type(option_match)))

         if option_match not in [Subscribe.MATCH_EXACT, Subscribe.MATCH_PREFIX, Subscribe.MATCH_WILDCARD]:
            raise ProtocolError("invalid value {} for 'match' option in SUBSCRIBE".format(option_match))

         match = option_match

      obj = Subscribe(request, topic, match)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.match and self.match != Subscribe.MATCH_EXACT:
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


   @staticmethod
   def parse(wmsg):
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

      obj = Subscribed(request, subscription)

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


   @staticmethod
   def parse(wmsg):
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

      obj = Unsubscribe(request, subscription)

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


   @staticmethod
   def parse(wmsg):
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

      obj = Unsubscribed(request)

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
      Message.__init__(self)
      self.subscription = subscription
      self.publication = publication
      self.args = args
      self.kwargs = kwargs
      self.publisher = publisher


   @staticmethod
   def parse(wmsg):
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
      details = check_or_raise_extra(wmsg[3], "'details' in EVENT")

      args = None
      if len(wmsg) > 4:
         args = wmsg[4]
         if type(args) != list:
            raise ProtocolError("invalid type {} for 'args' in EVENT".format(type(args)))

      kwargs = None
      if len(wmsg) > 5:
         kwargs = wmsg[5]
         if type(kwargs) != dict:
            raise ProtocolError("invalid type {} for 'kwargs' in EVENT".format(type(kwargs)))

      publisher = None
      if details.has_key('publisher'):

         detail_publisher = details['publisher']
         if type(detail_publisher) not in [int, long]:
            raise ProtocolError("invalid type {} for 'publisher' detail in EVENT".format(type(detail_publisher)))

         publisher = detail_publisher

      obj = Event(subscription,
                  publication,
                  args = args,
                  kwargs = kwargs,
                  publisher = publisher)

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

   def __init__(self,
                request,
                procedure,
                args = None,
                kwargs = None,
                timeout = None,
                receive_progress = None,
                discloseMe = None):
      """
      Message constructor.

      :param request: The WAMP request ID of this request.
      :type request: int
      :param procedure: The WAMP or application URI of the procedure which should be called.
      :type procedure: str
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
      self.receive_progress = receive_progress
      self.discloseMe = discloseMe


   @staticmethod
   def parse(wmsg):
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
      options = check_or_raise_extra(wmsg[2], "'options' in CALL")
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
         if type(option_timeout) not in [int, long]:
            raise ProtocolError("invalid type {} for 'timeout' option in CALL".format(type(option_timeout)))

         if option_timeout < 0:
            raise ProtocolError("invalid value {} for 'timeout' option in CALL".format(option_timeout))

         timeout = option_timeout

      receive_progress = None
      if options.has_key('receive_progress'):

         option_receive_progress = options['receive_progress']
         if type(option_receive_progress) != bool:
            raise ProtocolError("invalid type {} for 'receive_progress' option in CALL".format(type(option_receive_progress)))

         receive_progress = option_receive_progress

      discloseMe = None
      if options.has_key('disclose_me'):

         option_discloseMe = options['disclose_me']
         if type(option_discloseMe) != bool:
            raise ProtocolError("invalid type {} for 'disclose_me' option in CALL".format(type(option_discloseMe)))

         discloseMe = option_discloseMe

      obj = Call(request,
                 procedure,
                 args = args,
                 kwargs = kwargs,
                 timeout = timeout,
                 receive_progress = receive_progress,
                 discloseMe = discloseMe)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.timeout is not None:
         options['timeout'] = self.timeout

      if self.receive_progress is not None:
         options['receive_progress'] = self.receive_progress

      if self.discloseMe is not None:
         options['disclose_me'] = self.discloseMe

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
      return "WAMP CALL Message (request = {}, procedure = {}, args = {}, kwargs = {}, timeout = {}, receive_progress = {}, discloseMe = {})".format(self.request, self.procedure, self.args, self.kwargs, self.timeout, self.receive_progress, self.discloseMe)



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


   @staticmethod
   def parse(wmsg):
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
      options = check_or_raise_extra(wmsg[2], "'options' in CANCEL")

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

      obj = Cancel(request, mode = mode)

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
      return "WAMP CANCEL Message (request = {}, mode = '{}'')".format(self.request, self.mode)



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
      Message.__init__(self)
      self.request = request
      self.args = args
      self.kwargs = kwargs
      self.progress = progress


   @staticmethod
   def parse(wmsg):
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
      details = check_or_raise_extra(wmsg[2], "'details' in RESULT")

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

      obj = Result(request, args = args, kwargs = kwargs, progress = progress)

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
      return "WAMP RESULT Message (request = {}, args = {}, kwargs = {}, progress = {})".format(self.request, self.args, self.kwargs, self.progress)



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

   def __init__(self, request, procedure, pkeys = None, discloseCaller = None):
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
      self.discloseCaller = discloseCaller


   @staticmethod
   def parse(wmsg):
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
      options = check_or_raise_extra(wmsg[2], "'options' in REGISTER")
      procedure = check_or_raise_uri(wmsg[3], "'procedure' in REGISTER")

      pkeys = None
      discloseCaller = None

      if options.has_key('pkeys'):

         option_pkeys = options['pkeys']
         if type(option_pkeys) != list:
            raise ProtocolError("invalid type {} for 'pkeys' option in REGISTER".format(type(option_pkeys)))

         for pk in option_pkeys:
            if type(pk) not in [int, long]:
               raise ProtocolError("invalid type for value '{}' in 'pkeys' option in REGISTER".format(type(pk)))

         pkeys = option_pkeys


      if options.has_key('disclose_caller'):

         option_discloseCaller = options['disclose_caller']
         if type(option_discloseCaller) != bool:
            raise ProtocolError("invalid type {} for 'disclose_caller' option in REGISTER".format(type(option_discloseCaller)))

         discloseCaller = option_discloseCaller

      obj = Register(request, procedure, pkeys = pkeys, discloseCaller = discloseCaller)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.pkeys is not None:
         options['pkeys'] = self.pkeys

      if self.discloseCaller is not None:
         options['disclose_caller'] = self.discloseCaller

      return [Register.MESSAGE_TYPE, self.request, options, self.procedure]


   def __str__(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.__str__`
      """
      return "WAMP REGISTER Message (request = {}, procedure = {}, pkeys = {}, discloseCaller = {})".format(self.request, self.procedure, self.pkeys, self.discloseCaller)



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
      :param registration: The registration ID for the registered procedure (or procedure pattern).
      :type registration: int
      """
      Message.__init__(self)
      self.request = request
      self.registration = registration


   @staticmethod
   def parse(wmsg):
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

      obj = Registered(request, registration)

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


   @staticmethod
   def parse(wmsg):
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

      obj = Unregister(request, registration)

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


   @staticmethod
   def parse(wmsg):
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

      obj = Unregistered(request)

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
class Invocation(Message):
   """
   A WAMP `INVOCATION` message.

   Formats:
     * `[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict]`
     * `[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, CALL.Arguments|list]`
     * `[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, CALL.Arguments|list, CALL.ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 68
   """
   The WAMP message code for this type of message.
   """


   def __init__(self,
                request,
                registration,
                args = None,
                kwargs = None,
                timeout = None,
                receive_progress = None,
                caller = None,
                authid = None,
                authrole = None,
                authmethod = None):
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
      self.receive_progress = receive_progress
      self.caller = caller
      self.authid = authid
      self.authrole = authrole
      self.authmethod = authmethod


   @staticmethod
   def parse(wmsg):
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
      details = check_or_raise_extra(wmsg[3], "'details' in INVOCATION")

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
         if type(detail_timeout) not in [int, long]:
            raise ProtocolError("invalid type {} for 'timeout' detail in INVOCATION".format(type(detail_timeout)))

         if detail_timeout < 0:
            raise ProtocolError("invalid value {} for 'timeout' detail in INVOCATION".format(detail_timeout))

         timeout = detail_timeout

      receive_progress = None
      if details.has_key('receive_progress'):

         detail_receive_progress = details['receive_progress']
         if type(detail_receive_progress) != bool:
            raise ProtocolError("invalid type {} for 'receive_progress' detail in INVOCATION".format(type(detail_receive_progress)))

         receive_progress = detail_receive_progress

      caller = None
      if details.has_key('caller'):

         detail_caller = details['caller']
         if type(detail_caller) not in [int, long]:
            raise ProtocolError("invalid type {} for 'caller' detail in INVOCATION".format(type(detail_caller)))

         caller = detail_caller

      authid = None
      if details.has_key('authid'):

         detail_authid = details['authid']
         if type(detail_authid) not in [str, unicode]:
            raise ProtocolError("invalid type {} for 'authid' detail in INVOCATION".format(type(detail_authid)))

         authid = detail_authid

      authrole = None
      if details.has_key('authrole'):

         detail_authrole = details['authrole']
         if type(detail_authrole) not in [str, unicode]:
            raise ProtocolError("invalid type {} for 'authrole' detail in INVOCATION".format(type(detail_authrole)))

         authrole = detail_authrole

      authmethod = None
      if details.has_key('authmethod'):

         detail_authmethod = details['authmethod']
         if type(detail_authrole) not in [str, unicode]:
            raise ProtocolError("invalid type {} for 'authmethod' detail in INVOCATION".format(type(detail_authrole)))

         authmethod = detail_authmethod

      obj = Invocation(request,
                       registration,
                       args = args,
                       kwargs = kwargs,
                       timeout = timeout,
                       receive_progress = receive_progress,
                       caller = caller,
                       authid = authid,
                       authrole = authrole,
                       authmethod = authmethod)

      return obj

   
   def marshal(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessage.marshal`
      """
      options = {}

      if self.timeout is not None:
         options['timeout'] = self.timeout

      if self.receive_progress is not None:
         options['receive_progress'] = self.receive_progress

      if self.caller is not None:
         options['caller'] = self.caller

      if self.authid is not None:
         options['authid'] = self.authid

      if self.authrole is not None:
         options['authrole'] = self.authrole

      if self.authmethod is not None:
         options['authmethod'] = self.authmethod

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
      return "WAMP INVOCATION Message (request = {}, registration = {}, args = {}, kwargs = {}, timeout = {}, receive_progress = {}, caller = {}, authid = {}, authrole = {}, authmethod = {})".format(self.request, self.registration, self.args, self.kwargs, self.timeout, self.receive_progress, self.caller, self.authid, self.authrole, self.authmethod)



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


   @staticmethod
   def parse(wmsg):
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
      options = check_or_raise_extra(wmsg[2], "'options' in INTERRUPT")

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

      obj = Interrupt(request, mode = mode)

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
      return "WAMP INTERRUPT Message (request = {}, mode = '{}'')".format(self.request, self.mode)



@implementer(IMessage)
class Yield(Message):
   """
   A WAMP `YIELD` message.

   Formats:
     * `[YIELD, INVOCATION.Request|id, Options|dict]`
     * `[YIELD, INVOCATION.Request|id, Options|dict, Arguments|list]`
     * `[YIELD, INVOCATION.Request|id, Options|dict, Arguments|list, ArgumentsKw|dict]`
   """

   MESSAGE_TYPE = 70
   """
   The WAMP message code for this type of message.
   """


   def __init__(self, request, args = None, kwargs = None, progress = None):
      """
      Message constructor.

      :param request: The WAMP request ID of the original call.
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


   @staticmethod
   def parse(wmsg):
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
      options = check_or_raise_extra(wmsg[2], "'options' in YIELD")

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

      obj = Yield(request, args = args, kwargs = kwargs, progress = progress)

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
      return "WAMP YIELD Message (request = {}, args = {}, kwargs = {}, progress = {})".format(self.request, self.args, self.kwargs, self.progress)
