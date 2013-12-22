###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
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
   isBinary = Attribute("""Flag to indicate if serializer requires a binary clean transport (or if UTF8 transparency is sufficient).""")

   def serialize(self, obj):
      """
      Serialize an object to a byte string.

      :param obj: Object to serialize.
      :type obj: Any serializable type.

      :returns str -- Serialized byte string.
      """

   def unserialize(self, bytes):
      """
      Unserialize an object from a byte string.

      :param bytes: Object to serialize.
      :type bytes: Any serializable type.

      :returns obj -- Any type that can be unserialized.
      """


class IWampMessage(Interface):
   """
   A WAMP message.
   """

   # @classmethod
   # def parse(Klass, wmsg):
   #    """
   #    Verifies and parses an unserialized raw message into an actual WAMP message instance.

   #    :param wmsg: The unserialized raw message.
   #    :type wmsg: list
   #    :returns obj -- An instance of this class.
   #    """

   
   def serialize(serializer):
      """
      Serialize this object into a wire level bytestring representation.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`
      """

   def __eq__(other):
      """
      """

   def __ne__(other):
      """
      """

   def __str__():
      """
      Returns text representation of this message.

      :returns str -- Human readable representation (e.g. for logging or debugging purposes).
      """

#   serializer = Attribute("""The WAMP message serializer for this channel.""")



class IMessageChannel(Interface):

   def send(message):
      """
      """

   def isOpen():
      """
      """

   def close():
      """
      """

   def abort():
      """
      """


class IMessageChannelHandler(Interface):

   def onOpen(channel):
      """
      """

   def onMessage(message):
      """
      """

   def onClose():
      """
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


# class IWampPublishOptions(Interface):

#    excludeMe = Attribute("Exclude me, the publisher, from receiving the event (even though I may be subscribed).")



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
