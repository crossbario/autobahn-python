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



class SessionDetails:
   """
   Provides details for a WAMP session, provided in
   :func:`autobahn.wamp.interfaces.IAppSession.onSessionOpen`.
   """

   def __init__(self, me, peer):
      """
      Ctor.

      :param me: WAMP session ID of this session.
      :type me: int
      :param peer: WAMP session ID of the peer session.
      :type peer: int
      """
      self.me = me
      self.peer = peer



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
      assert(type(details_arg) == str)

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
                excludeMe = None,
                exclude = None,
                eligible = None,
                discloseMe = None):
      """
      Constructor.
      
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
      assert(excludeMe is None or type(excludeMe) == bool)
      assert(exclude is None or (type(exclude) == list and all(type(x) in [int, long] for x in exclude)))
      assert(eligible is None or (type(eligible) == list and all(type(x) in [int, long] for x in eligible)))
      assert(discloseMe is None or type(discloseMe) == bool)

      self.options = {
         'excludeMe': excludeMe,
         'exclude': exclude,
         'eligible': eligible,
         'discloseMe': discloseMe
      }



class RegisterOptions:
   """
   Used to provide options for subscribing in
   :func:`autobahn.wamp.interfaces.ICallee.register`.
   """

   def __init__(self, details_arg = None, pkeys = None):
      """
      Ctor.

      :param details_arg: When invoking the endpoint, provide call details
                          in this keyword argument to the callable.
      :type details_arg: str
      """
      assert(type(details_arg) == str)
      self.details_arg = details_arg
      self.options = {'pkeys': pkeys}



class CallDetails:
   """
   Provides details on a call when an endpoint previously
   registered is being called and opted to receive call details.
   """

   def __init__(self, progress = None, caller = None):
      """
      Ctor.

      :param progress: A callable that will receive progressive call results.
      :type progress: callable
      :param caller: The WAMP session ID of the caller, if the latter is disclosed.
      :type caller: int
      """
      self.progress = progress
      self.caller = caller



class CallOptions:
   """
   Used to provide options for subscribing in
   :func:`autobahn.wamp.interfaces.ICaller.call`.
   """

   def __init__(self,
                onProgress = None,
                timeout = None,
                discloseMe = None,
                runOn = None,
                runMode = None):
      """
      Constructor.

      :param procedure: The URI of the remote procedure to be called, e.g. "com.myapp.hello".
      :type procedure: str
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








class Registration:
   """
   """
   def __init__(self, id, procedure, endpoint):
      self._id = id
      self._procedure = procedure
      self._endpoint = endpoint
      self._isActive = True



class Invocation:
   """
   """
   def __init__(self, caller = None):
      self.caller = caller

   def progress(self, *args, **kwargs):
      pass



class Subscription:
   """
   """
   def __init__(self, id, topic):
      self._id = id
      self._topic = topic
      self._watchers = []
      self._isActive = True


   def watch(self, watcher):
      """
      Adds a watcher to the subscription.

      If the given watcher is already watching, silently ignore the call. Otherwise
      add the watcher (which must be a callable) to the list of watchers.

      :param watcher: The watcher who should be notified upon receiving events on the
                      given subscription. This must be a callable which will get called
                      with the topic and event payload as arguments upon receiving of
                      events.
      :type watcher: callable
      """
      assert(self._isActive)
      assert(callable(watcher))
      if not watcher in self._watchers:
         self._watchers.append(watcher)


   def unwatch(self, watcher = None):
      """
      Remove a watcher from the subscription.

      If the given watcher is no watching, silently ignore the call. Otherwise
      remote the watcher from the list of watchers.

      :param watcher: The watcher who should be removed from the list of current watchers
                      or None to remove all watchers.
      :type watcher: callable
      """
      assert(self._isActive)
      if watcher:
         if watcher in self._watchers:
            self._watchers.remove(watcher)
      else:
         self._watchers = []


   def notify(self, event):
      """
      Notify all current watcher for this subscription.

      Watchers will be notified in the order how they were added to this subscription.

      :param topic: The URI of the topic.
      :type topic: str
      :param event: The event (payload).
      :type event: obj
      """
      assert(self._isActive)
      assert(isinstance(event, Event))
      for watcher in self._watchers:
         watcher(event)





