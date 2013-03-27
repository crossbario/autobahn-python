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

import re

from twisted.python import log
from trie import StringTrie as Trie

__all__ = ['SubscriptionMapSimple', 'SubscriptionMapCached']


class SubscriptionMap2:
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
      if options is not None and options.has_key('match') and options['match'] == 'prefix':
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


class SubscriptionMap3:
   """
   Maintains topic subscriptions on broker-side.

   For prefix subscriptions, use this stuff:
     - https://bitbucket.org/gsakkis/pytrie
     - https://github.com/kmike/datrie
   """

   def __init__(self, onClientSubscribed = None, onClientUnsubscribed = None, debugWamp = False):
      self.patterns = {}
      self.subscriptions = {}

      ## subscribe/unsubscribe hooks
      self.onClientSubscribed = onClientSubscribed
      self.onClientUnsubscribed = onClientUnsubscribed

      ## debug WAMP flag
      self.debugWamp = debugWamp


   def subscribe(self, proto, topicUri, options = None):
      """
      Add a subscriber to the subscription map.
      """
      if options is not None and options.has_key('match') and options['match'] in ['exact', 'prefix']:
         patterntype = options['match']
      else:
         patterntype = 'exact'

      patternkey = (patterntype, topicUri)
      if not self.patterns.has_key(patternkey):
         self.patterns[patternkey] = set()
         if self.debugWamp:
            log.msg("subscriptions map created for topic pattern %s" % str(patternkey))

      if not proto in self.patterns[patternkey]:
         self.patterns[patternkey].add(proto)
         if self.debugWamp:
            log.msg("subscribed peer %s on topic pattern %s" % (proto.peerstr, str(patternkey)))
         if self.onClientSubscribed:
            self.onClientSubscribed(proto, topicUri, options)
      else:
         if self.debugWamp:
            log.msg("peer %s already subscribed on topic pattern %s" % (proto.peerstr, str(patternkey)))


   def unsubscribe(self, proto, topicUri = None):
      """
      Remove a subscriber from the subscription map.

      FIXME: unsubscribe also from self.prefixSubscriptions
      """
      return
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
      if not self.subscriptions.has_key(topicUri):
         self.subscriptions[topicUri] = set()
         for ((patterntype, pattern), protos) in self.patterns.items():
            if (patterntype == 'exact' and topicUri == pattern) or \
               (patterntype == 'prefix' and topicUri.startswith(pattern)):
                  self.subscriptions[topicUri].update(protos)
      return self.subscriptions[topicUri]



class SubscriptionMapBase:

   def __init__(self):
      self.patterns = {}


   def keyhash(self, patternType, topicPattern):
      return str((patternType, topicPattern))


   def add(self, obj, patternType, topicPattern):
      key = self._key(patternType, topicPattern)
      if not self.patterns.has_key(key):
         self.patterns[key] = (self._extra(patternType, topicPattern), set())
         patternAdded = True
      else:
         patternAdded = False
      if not obj in self.patterns[key][1]:
         self.patterns[key][1].add(obj)
         objAdded = True
      else:
         objAdded = False
      return (patternAdded, objAdded)


   def removeObj(self, obj):
      patternsRemoved = []
      for (key, (_, objs)) in self.patterns.items():
         if obj in objs:
            objs.discard(obj)
            if len(objs) == 0:
               del self.patterns[key]
               patternsRemoved.append((key, True))
            else:
               patternsRemoved.append((key, False))
      return patternsRemoved


   def removePattern(self, patternType, topicPattern):
      key = self._key(patternType, topicPattern)
      if self.patterns.has_key(key):
         objsRemoved = self.patterns[key][1]
         del self.patterns[key]
         return objsRemoved
      else:
         return set()


   def remove(self, obj, patternType, topicPattern):
      key = self._key(patternType, topicPattern)
      if self.patterns.has_key(key) and obj in self.patterns[key][1]:
         self.patterns[key][1].discard(obj)
         if len(self.patterns[key][1]) == 0:
            del self.patterns[key]
            return (key, True)
         else:
            return (key, False)
      else:
         return ((None, None), False)



class SubscriptionMapSimple(SubscriptionMapBase):

   PATTERN_TYPES = ['exact']

   def __init__(self):
      SubscriptionMapBase.__init__(self)
      self.subscriptions = self.patterns


   def _key(self, patternType, topicPattern):
      return topicPattern


   def _extra(self, patternType, topicPattern):
      return None


   def get(self, topic):
      return self.subscriptions.get(topic, (None, set()))[1]



class SubscriptionMapCached(SubscriptionMapBase):

   PATTERN_TYPES = ['exact', 'prefix', 'regex']

   def __init__(self):
      SubscriptionMapBase.__init__(self)
      self.subscriptions = {}


   def _key(self, patternType, topicPattern):
      return (patternType, topicPattern)


   def _extra(self, patternType, topicPattern):
      if patternType == 'regex':
         return re.compile(topicPattern)
      else:
         return None


   def get(self, topic):
      if not self.subscriptions.has_key(topic):
         self.subscriptions[topic] = []
         for ((patternType, topicPattern), (extra, objs)) in self.patterns.items():
            if (patternType == 'exact' and topic == topicPattern) or \
               (patternType == 'prefix' and topic.startswith(topicPattern) or \
               (patternType == 'regex' and extra.match(topic))):
                  self.subscriptions[topic].append(objs)
      res = set()
      for s in self.subscriptions[topic]:
         res.update(s)
      return res
