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


class SessionInfo:

   def __init__(self, me, peer):
      self.me = me
      self.peer = peer



class Registration:
   """
   """
   def __init__(self, id, procedure, endpoint):
      self._id = id
      self._procedure = procedure
      self._endpoint = endpoint
      self._isActive = True



class CallOptions:
   """
   Wrapper allowing to specify a remote procedure to be called while providing
   details on exactly how the call should be performed.
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

      self.onProgress = onProgress
      self.timeout = timeout
      self.discloseMe = discloseMe
      self.runOn = runOn
      self.runMode = runMode



class CallResult:
   """
   Wrapper for WAMP remote procedure call results that contain multiple positional
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



class Invocation:
   """
   """
   def __init__(self, caller = None):
      self.caller = caller

   def progress(self, *args, **kwargs):
      pass



class SubscribeOptions:
   """
   """
   def __init__(self, match = None):
      assert(match is None or (type(match) == str and match in ['exact', 'prefix', 'wildcard']))
      self.match = match



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



class Publish:
   """
   Wrapper allowing to specify a topic to be published to while providing
   details on exactly how the publishing should be performed.
   """

   def __init__(self,
                topic,
                excludeMe = None,
                exclude = None,
                eligible = None,
                discloseMe = None):
      """
      Constructor.
      
      :param topic: The URI of the topic to publish to, e.g. "com.myapp.mytopic1".
      :type topic: str
      :param discloseMe: Request to disclose the identity of the caller (it's WAMP session ID)
                         to Callees. Note that a Dealer, depending on Dealer configuration, might
                         reject the request, or might disclose the Callee's identity without
                         a request to do so.
      :type discloseMe: bool
      """
      assert(excludeMe is None or type(excludeMe) == bool)
      assert(exclude is None or (type(exclude) == list and all(type(x) == int for x in exclude)))
      assert(eligible is None or (type(eligible) == list and all(type(x) == int for x in eligible)))
      assert(discloseMe is None or type(discloseMe) == bool)

      self.topic = topic
      self.excludeMe = excludeMe
      self.exclude = exclude
      self.eligible = eligible
      self.discloseMe = discloseMe



class Event:
   def __init__(self, topic, payload, publication, publisher = None):
      self.topic = topic
      self.payload = payload
      self.publication = publication
      self.publisher = publisher

