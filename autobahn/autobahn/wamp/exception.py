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

__all__ = (
   'Error',
   'SessionNotReady',
   'SerializationError',
   'ProtocolError',
   'TransportLost',
   'ApplicationError',
   'NotAuthorized',
   'InvalidUri',
)

from autobahn.wamp import error



class Error(RuntimeError):
   """
   Base class for all exceptions related to WAMP.
   """
   def __init__(self, reason):
      """

      :param reason: Description of WAMP error that occurred (for logging purposes).
      :type reason: unicode
      """
      RuntimeError.__init__(self, reason)



class SessionNotReady(Error):
   """
   The application tried to perform a WAMP interaction, but the
   session is not yet fully established.
   """



class SerializationError(Error):
   """
   Exception raised when the WAMP serializer could not serialize the
   application payload (``args`` or ``kwargs`` for ``CALL``, ``PUBLISH``, etc).
   """



class ProtocolError(Error):
   """
   Exception raised when WAMP protocol was violated. Protocol errors
   are fatal and are handled by the WAMP implementation. They are
   not supposed to be handled at the application level.
   """



class TransportLost(Error):
   """
   Exception raised when the transport underlying the WAMP session
   was lost or is not connected.
   """
   def __init__(self):
      Error.__init__(self, u"WAMP transport lost")



class ApplicationError(Error):
   """
   Base class for all exceptions that can/may be handled
   at the application level.
   """

   INVALID_URI = u"wamp.error.invalid_uri"
   """
   Peer provided an incorrect URI for a URI-based attribute of a WAMP message
   such as a realm, topic or procedure.
   """

   NO_SUCH_PROCEDURE = u"wamp.error.no_such_procedure"
   """
   A Dealer could not perform a call, since not procedure is currently registered
   under the given URI.
   """

   PROCEDURE_ALREADY_EXISTS = u"wamp.error.procedure_already_exists"
   """
   A procedure could not be registered, since a procedure with the given URI is
   already registered.
   """

   NO_SUCH_REGISTRATION = u"wamp.error.no_such_registration"
   """
   A Dealer could not perform a unregister, since the given registration is not active.
   """

   NO_SUCH_SUBSCRIPTION = u"wamp.error.no_such_subscription"
   """
   A Broker could not perform a unsubscribe, since the given subscription is not active.
   """

   INVALID_ARGUMENT = u"wamp.error.invalid_argument"
   """
   A call failed, since the given argument types or values are not acceptable to the
   called procedure - in which case the *Callee* may throw this error. Or a Router
   performing *payload validation* checked the payload (``args`` / ``kwargs``) of a call,
   call result, call error or publish, and the payload did not conform.
   """

   ## FIXME: this currently isn't used neither in Autobahn nor Crossbar. Check!
   SYSTEM_SHUTDOWN = u"wamp.error.system_shutdown"
   """
   The *Peer* is shutting down completely - used as a ``GOODBYE`` (or ``ABORT``) reason.
   """

   ## FIXME: this currently isn't used neither in Autobahn nor Crossbar. Check!
   CLOSE_REALM = u"wamp.error.close_realm"
   """
   The *Peer* want to leave the realm - used as a ``GOODBYE`` reason.
   """

   ## FIXME: this currently isn't used neither in Autobahn nor Crossbar. Check!
   GOODBYE_AND_OUT = u"wamp.error.goodbye_and_out"
   """
   A *Peer* acknowledges ending of a session - used as a ``GOOBYE`` reply reason.
   """
   
   NOT_AUTHORIZED = u"wamp.error.not_authorized"
   """
   A call, register, publish or subscribe failed, since the session is not authorized
   to perform the operation.
   """

   AUTHORIZATION_FAILED = u"wamp.error.authorization_failed"
   """
   A Dealer or Broker could not determine if the *Peer* is authorized to perform
   a join, call, register, publish or subscribe, since the authorization operation
   *itself* failed. E.g. a custom authorizer did run into an error.
   """

   NO_SUCH_REALM = u"wamp.error.no_such_realm"
   """
   Peer wanted to join a non-existing realm (and the *Router* did not allow to auto-create
   the realm).
   """

   NO_SUCH_ROLE = u"wamp.error.no_such_role"
   """
   A *Peer* was to be authenticated under a Role that does not (or no longer) exists on the Router.
   For example, the *Peer* was successfully authenticated, but the Role configured does not
   exists - hence there is some misconfiguration in the Router.
   """

   ## FIXME: this currently isn't used neither in Autobahn nor Crossbar. Check!
   CANCELED = u"wamp.error.canceled"
   """
   A Dealer or Callee canceled a call previously issued (WAMP AP).
   """

   ## FIXME: this currently isn't used neither in Autobahn nor Crossbar. Check!
   OPTION_DISALLOWED_DISCLOSE_ME = u"wamp.error.option_disallowed.disclose_me"
   """
   A Router rejected client request to disclose its identity (WAMP AP).
   """

   ## FIXME: this currently isn't used neither in Autobahn nor Crossbar. Check!
   NO_ELIGIBLE_CALLEE = u"wamp.error.no_eligible_callee"
   """
   A *Dealer* could not perform a call, since a procedure with the given URI is registered,
   but *Callee Black- and Whitelisting* and/or *Caller Exclusion* lead to the
   exclusion of (any) *Callee* providing the procedure (WAMP AP).
   """


   def __init__(self, error, *args, **kwargs):
      """

      :param error: The URI of the error that occurred, e.g. ``wamp.error.not_authorized``.
      :type error: unicode
      """
      Exception.__init__(self, *args)
      self.kwargs = kwargs
      self.error = error


   def __str__(self):
      if self.kwargs and 'traceback' in self.kwargs:
         tb = ':\n' + '\n'.join(self.kwargs.pop('traceback')) + '\n'
         self.kwargs['traceback'] = '...'
      else:
         tb = ''
      return "ApplicationError('{0}', args = {1}, kwargs = {2}){3}".format(self.error, self.args, self.kwargs, tb)



@error(ApplicationError.NOT_AUTHORIZED)
class NotAuthorized(Exception):
   """
   Not authorized to perform the respective action.
   """


@error(ApplicationError.INVALID_URI)
class InvalidUri(Exception):
   """
   The URI for a topic, procedure or error is not a valid WAMP URI.
   """
