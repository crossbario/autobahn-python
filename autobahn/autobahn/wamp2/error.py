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


class Error(RuntimeError):
   """
   Base class for all exceptions related to WAMP.
   """
   def __init__(self, reason):
      """
      Constructor.

      :param reason: Description of WAMP error that occurred (for logging purposes).
      :type reason: str
      """
      RuntimeError.__init__(self, reason)



class ProtocolError(Error):
   """
   Exception raised when WAMP protocol was violated. Protocol errors
   are fatal and are handled by the WAMP implementation. They are
   not supposed to be handled at the application level.
   """



class ApplicationError(Error):
   """
   Base class for all exceptions that can/may be handled
   at the application level.
   """
   NOT_AUTHORIZED             = "wamp.error.not_authorized"
   INVALID_ARGUMENT           = "wamp.error.invalid_argument"
   INVALID_TOPIC              = "wamp.error.invalid_topic"
   DISCLOSE_ME_NOT_ALLOWED    = "wamp.error.disclose_me.not_allowed"
   PROCEDURE_ALREADY_EXISTS   = "wamp.error.procedure_already_exists"
   NO_SUCH_REGISTRATION       = "wamp.error.no_such_registration"
   NO_SUCH_SUBSCRIPTION       = "wamp.error.no_such_subscription"
   NO_SUCH_PROCEDURE          = "wamp.error.no_such_procedure"

   def __init__(self, error, reason = None):
      """
      Constructor.

      :param error: The URI of the error that occurred, e.g. "wamp.error.not_authorized".
      :type error: str
      """
      if reason:
         Error.__init__(self, "application error with URI '{}' - '{}'".format(error, reason))
      else:
         Error.__init__(self, "application error with URI '{}'".format(error))
      self.error = error



class CallError(ApplicationError):
   """
   Wrapper for WAMP remote procedure call errors. 
   """

   def __init__(self, error, problem):
      """
      Constructor.

      :param error: The URI of the error that occurred, e.g. "com.myapp.error.no_such_user".
      :type error: str
      :param problem: Any application-level details for the error that occurred.
      :type problem: obj
      """
      ApplicationError.__init__(self, error)
      self.problem = problem
