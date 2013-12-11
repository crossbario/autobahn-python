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


import zope
from zope.interface import Interface, Attribute


class ISerializer(Interface):
   """
   Serialization and unserialization.
   """

   def serialize(self, obj):
      """
      Serialize an object to a byte string.

      :param obj: Object to serialize.
      :type obj: Any serializable type.

      :returns str -- Serialized byte string.
      """

   def unserialize(self, bytes, isbinar):
      """
      Unserialize an object from a byte string.

      :param bytes: Object to serialize.
      :type bytes: Any serializable type.

      :returns obj -- Any type that can be unserialized.
      """


class IWampDealer(Interface):
   """
   """

   def register(self, endpoint, obj):
      """
      """

   def registerMethod(self, endpoint, obj, method):
      """
      """

   def registerProcedure(self, endpoint, procedure):
      """
      """

   def unregister(self, endpoint):
      """
      """


class IWampBroker(Interface):
   """
   """

   def register(self, topic, prefix = False, publish = True, subscribe = True):
      """
      """

   def unregister(self, topic):
      """
      """


class IWampPublishOptions(Interface):

   excludeMe = Attribute("Exclude me, the publisher, from receiving the event (even though I may be subscribed).")



class IWampSession(Interface):
   """
   """

   def call(self, *args):
      """
      """

   def subscribe(self, topic, handler):
      """
      """

   def unsubscribe(self, topic, handler = None):
      """
      """

   def publish(self, topic, event,
               excludeMe = None,
               exclude = None,
               eligible = None,
               discloseMe = None):
      """
      """

   def setDealer(self, dealer = None):
      """
      """

   def setBroker(self, broker = None):
      """
      """
