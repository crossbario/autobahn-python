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


class HelloReturn:
   pass



class Accept(HelloReturn):
   def __init__(self, authid = None, authrole = None, authmethod = None):
      self.authid = authid
      self.authrole = authrole
      self.authmethod = authmethod



class Deny(HelloReturn):
   def __init__(self, reason = "wamp.error.not_authorized", message = None):
      self.reason = reason
      self.message = message



class Challenge(HelloReturn):
   def __init__(self, method, extra = {}):
      self.method = method
      self.extra = extra



class HelloDetails:
   def __init__(self, roles = None, authmethods = None):
      self.roles = roles
      self.authmethods = authmethods



class SessionDetails:
   """
   Provides details for a WAMP session, provided in
   :func:`autobahn.wamp.interfaces.IAppSession.onSessionOpen`.
   """

   def __init__(self, session):
      """
      Ctor.

      :param session: WAMP session ID of this session.
      :type session: int
      """
      self.session = session



class CloseDetails:
   """
   Provides details on closing of a WAMP session, provided in
   :func:`autobahn.wamp.interfaces.IAppSession.onSessionClose`.
   """

   def __init__(self, reason = None, message = None):
      self.reason = reason
      self.message = message



class SubscribeOptions:
   """
   Used to provide options for subscribing in
   :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`.
   """

   def __init__(self, match = None, details_arg = None):
      """
      :param match: The topic matching method to be used for the subscription.
      :type match: str
      :param details_arg: When invoking the handler, provide event details
                          in this keyword argument to the callable.
      :type details_arg: str
      """
      assert(match is None or (type(match) == str and match in ['exact', 'prefix', 'wildcard']))
      assert(details_arg is None or type(details_arg) == str)

      self.details_arg = details_arg
      self.options = {'match': match}



class EventDetails:
   """
   Provides details on an event when calling an event handler
   previously registered.
   """
   def __init__(self, publication, publisher = None):
      """
      Ctor.

      :param publication: The publication ID of the event (always present).
      :type publication: int
      :param publisher: The WAMP session ID of the original publisher of this event.
      :type publisher: int
      """
      self.publication = publication
      self.publisher = publisher



class PublishOptions:
   """
   Used to provide options for subscribing in
   :func:`autobahn.wamp.interfaces.IPublisher.publish`.
   """

   def __init__(self,
                acknowledge = None,
                excludeMe = None,
                exclude = None,
                eligible = None,
                discloseMe = None):
      """
      Constructor.
      
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
      assert(acknowledge is None or type(acknowledge) == bool)
      assert(excludeMe is None or type(excludeMe) == bool)
      assert(exclude is None or (type(exclude) == list and all(type(x) in [int, long] for x in exclude)))
      assert(eligible is None or (type(eligible) == list and all(type(x) in [int, long] for x in eligible)))
      assert(discloseMe is None or type(discloseMe) == bool)

      self.options = {
         'acknowledge': acknowledge,
         'excludeMe': excludeMe,
         'exclude': exclude,
         'eligible': eligible,
         'discloseMe': discloseMe
      }



class RegisterOptions:
   """
   Used to provide options for registering in
   :func:`autobahn.wamp.interfaces.ICallee.register`.
   """

   def __init__(self, details_arg = None, pkeys = None, discloseCaller = None):
      """
      Ctor.

      :param details_arg: When invoking the endpoint, provide call details
                          in this keyword argument to the callable.
      :type details_arg: str
      """
      assert(details_arg is None or type(details_arg) == str)
      self.details_arg = details_arg
      self.options = {
         'pkeys': pkeys,
         'discloseCaller': discloseCaller
      }



class CallDetails:
   """
   Provides details on a call when an endpoint previously
   registered is being called and opted to receive call details.
   """

   def __init__(self, progress = None, caller = None, authid = None, authrole = None, authmethod = None):
      """
      Ctor.

      :param progress: A callable that will receive progressive call results.
      :type progress: callable
      :param caller: The WAMP session ID of the caller, if the latter is disclosed.
      :type caller: int
      :param authid: The authentication ID of the caller.
      :type authid: str
      :param authrole: The authentication role of the caller.
      :type authrole: str
      """
      self.progress = progress
      self.caller = caller
      self.authid = authid
      self.authrole = authrole
      self.authmethod = authmethod

   def __str__(self):
      return "CallDetails(progress = {}, caller = {}, authid = {}, authrole = {}, authmethod = {})".format(self.progress, self.caller, self.authid, self.authrole, self.authmethod)



class CallOptions:
   """
   Used to provide options for calling with :func:`autobahn.wamp.interfaces.ICaller.call`.
   """

   def __init__(self,
                onProgress = None,
                timeout = None,
                discloseMe = None,
                runOn = None):
      """
      Constructor.

      :param onProgress: A callback that will be called when the remote endpoint
                         called yields interim call progress results.
      :type onProgress: a callable
      :param timeout: Time in seconds after which the call should be automatically cancelled.
      :type timeout: float
      :param discloseMe: Request to disclose the identity of the caller (it's WAMP session ID)
                         to Callees. Note that a Dealer, depending on Dealer configuration, might
                         reject the request, or might disclose the Callee's identity without
                         a request to do so.
      :type discloseMe: bool
      :param runOn: If present (non-None), indicates a distributed call. Distributed calls allows
                    to run a call issued by a Caller on one or more endpoints implementing the
                    called procedure. Permissible value are: "all", "any" and "partition".
                    If `runOne == "partition"`, then `runPartitions` MUST be present.
      :type runOn: str
      """
      assert(onProgress is None or callable(onProgress))
      assert(timeout is None or (type(timeout) in [int, float] and timeout > 0))
      assert(discloseMe is None or type(discloseMe) == bool)
      assert(runOn is None or (type(runOn) == str and runOn in ["all", "any", "partition"]))

      self.options = {
         'timeout': timeout,
         'discloseMe': discloseMe
      }

      self.onProgress = onProgress
      if onProgress:
         self.options['receive_progress'] = True



class CallResult:
   """
   Wrapper for remote procedure call results that contain multiple positional
   return values or keyword return values.
   """

   def __init__(self, *results, **kwresults):
      """
      Constructor.

      :param results: The positional result values.
      :type results: list
      :param kwresults: The keyword result values.
      :type kwresults: dict
      """
      self.results = results
      self.kwresults = kwresults

   def __str__(self):
      return "CallResult(results = {}, kwresults = {})".format(self.results, self.kwresults)
