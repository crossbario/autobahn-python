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

from twisted.python import log
from trie import StringTrie as Trie


class SubscriptionMap:
   """
   Maintains topic subscriptions on broker-side.

   For prefix subscriptions, use this stuff:
     - https://bitbucket.org/gsakkis/pytrie
     - https://github.com/kmike/datrie
   """

   def __init__(self, onClientSubscribed = None, onClientUnsubscribed = None, debugWamp = False):
      ## non-prefix subscriptions
      self.subscriptions = {}

      ## prefix subscriptions
      self.prefixSubscriptions = Trie()

      ## subscribe/unsubscribe hooks
      self.onClientSubscribed = onClientSubscribed
      self.onClientUnsubscribed = onClientUnsubscribed

      ## debug WAMP flag
      self.debugWamp = debugWamp


   def subscribe(self, proto, topicUri, options = None):
      """
      Add a subscriber to the subscription map.
      """
      if options is not None and options.has_key('matchByPrefix') and options['matchByPrefix']:
         ## prefix subscription
         ##
         subscriptions = self.prefixSubscriptions
      else:
         ## plain (non-prefix) subscriptions
         ##
         subscriptions = self.subscriptions

      if not subscriptions.has_key(topicUri):
         subscriptions[topicUri] = set()
         if self.debugWamp:
            log.msg("subscriptions map created for topic %s" % topicUri)
      if not proto in subscriptions[topicUri]:
         subscriptions[topicUri].add(proto)
         if self.debugWamp:
            log.msg("subscribed peer %s on topic %s" % (proto.peerstr, topicUri))
         if self.onClientSubscribed:
            self.onClientSubscribed(proto, topicUri, options)
      else:
         if self.debugWamp:
            log.msg("peer %s already subscribed on topic %s" % (proto.peerstr, topicUri))


   def unsubscribe(self, proto, topicUri = None):
      """
      Remove a subscriber from the subscription map.

      FIXME: unsubscribe also from self.prefixSubscriptions
      """
      if topicUri:
         if self.subscriptions.has_key(topicUri) and proto in self.subscriptions[topicUri]:
            self.subscriptions[topicUri].discard(proto)
            if self.debugWamp:
               log.msg("unsubscribed peer %s from topic %s" % (proto.peerstr, topicUri))
            if len(self.subscriptions[topicUri]) == 0:
               del self.subscriptions[topicUri]
               if self.debugWamp:
                  log.msg("topic %s removed from subscriptions map - no one subscribed anymore" % topicUri)
            if self.onClientUnsubscribed:
               self.onClientUnsubscribed(proto, topicUri)
         else:
            if self.debugWamp:
               log.msg("peer %s not subscribed on topic %s" % (proto.peerstr, topicUri))
      else:
         for topicUri, subscribers in self.subscriptions.items():
            if proto in subscribers:
               subscribers.discard(proto)
               if self.debugWamp:
                  log.msg("unsubscribed peer %s from topic %s" % (proto.peerstr, topicUri))
               if len(subscribers) == 0:
                  del self.subscriptions[topicUri]
                  if self.debugWamp:
                     log.msg("topic %s removed from subscriptions map - no one subscribed anymore" % topicUri)
               if self.onClientUnsubscribed:
                  self.onClientUnsubscribed(proto, topicUri)
         if self.debugWamp:
            log.msg("unsubscribed peer %s from all topics" % (proto.peerstr))


   def getSubscribers(self, topicUri):
      """
      Get all current subscribers for topic.
      """
      ## get non-prefix subscribers
      ds = self.subscriptions.get(topicUri, set())

      ## add prefix subscribers
      for d in self.prefixSubscriptions.iter_prefix_values(topicUri):
         ds.update(d)

      return ds
