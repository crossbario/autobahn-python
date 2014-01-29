###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
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

from zope.interface import Interface, Attribute

## FIXME: rework for ABCs


class ITracker(Interface):
   """
   """
   tracker = Attribute("The WAMP URI of the trackable")
   tracked = Attribute("The target object tracked with this tracker.")

   def track(key = None):
      """
      """



class IMessage(Interface):
   """
   """
   binary  = Attribute("Flag indicating whether payload is binary.")
   priority = Attribute("Priority of message.")
   factory = Attribute("The message factory this message was created by.")
   channel = Attribute("The channel this message was created on.")
   tracker = Attribute("Optional timestamp and statistics tracker - an object that implements ITracker.")



class IInboundMessage(IMessage):
   """
   """

   def on_begin():
      """
      """

   def resume():
      """
      Resume receiving data for message.
      """

   def on_data(payload):
      """
      """

   def pause():
      """
      Pause receiving data for message.
      """

   def on_end():
      """
      """



class IOutboundMessage(IMessage):
   """
   """

   def begin():
      """
      """

   def on_resume():
      """
      Called when sending data should be resumed.
      """

   def send(payload):
      """
      """

   def on_pause():
      """
      Called when sending data should be paused.
      """

   def end():
      """
      """



class IMessageFactory(Interface):
   """
   """
   is_running = Attribute("True if factory is running.")
   factory = Attribute("The channel factory that this channel was created by.")
   tracker = Attribute("Optional timestamp and statistics tracker - an object that implements ITracker.")

   def on_start():
      """
      """

   def __call__(is_inbound = True):
      """
      Returns an object that implements IMessage.
      """

   def recycle(message):
      """
      """

   def stop():
      """
      """

   def on_stop():
      """
      """



class IMessageChannel(Interface):
   """
   """
   inbound = Attribute("The message factory for inbound messages.")
   outbound = Attribute("The message factory for outbound messages.")
   factory = Attribute("The channel factory that this channel was created by.")
   tracker = Attribute("Optional timestamp and statistics tracker - an object that implements ITracker.")

   def on_open():
      """
      """

   def send(is_binary = False, no_compress = False, priority = 0):
      """
      Returns an object implementing IOutboundMessage.
      """

   def on_message(self, message):
      """
      :param message: An object implementing IInboundMessage.
      :type message: IInboundMessage
      """

   def close(abort = False):
      """
      """

   def on_close(was_clean):
      """
      """



class IMessageChannelFactory(Interface):
   """
   """
   is_running = Attribute("True if factory is running.")
   node = Attribute("The node this message channel factory was added to.")
   tracker = Attribute("Optional timestamp and statistics tracker - an object that implements ITracker.")

   def on_start():
      """
      """

   def __call__():
      """
      Returns an object that implements IMessageChannel.
      """

   def recycle(factory):
      """
      """

   def stop():
      """
      """

   def on_stop():
      """
      """



class IMessagingNode(Interface):
   """
   """
   tracker = Attribute("Optional timestamp and statistics tracker - an object that implements ITracker.")

   def add(factory):
      """
      Add a message channel factory to this node.

      :param factory: The message channel factory to add to this node.
      :type factory: An object that implements IMessageChannelFactory
      """

   def remove(factory):
      """
      """
