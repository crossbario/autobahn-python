/******************************************************************************
 *
 *  Copyright 2011 Tavendo GmbH
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 ******************************************************************************/

package de.tavendo.autobahn;

/**
 * The master thread and the background reader/writer threads communicate
 * using these messages for Autobahn WAMP connections.
 */
public class AutobahnMessage {

   public static final int MESSAGE_TYPE_PREFIX = 1;
   public static final int MESSAGE_TYPE_CALL = 2;
   public static final int MESSAGE_TYPE_CALL_RESULT = 3;
   public static final int MESSAGE_TYPE_CALL_ERROR = 4;
   public static final int MESSAGE_TYPE_SUBSCRIBE = 5;
   public static final int MESSAGE_TYPE_UNSUBSCRIBE = 6;
   public static final int MESSAGE_TYPE_PUBLISH = 7;
   public static final int MESSAGE_TYPE_EVENT = 8;


   /**
    * RPC request message.
    * Client-to-server message.
    */
   public static class Call {
      public String mCallId;
      public String mProcUri;
      public Object[] mArgs;

      public Call(String callId, String procUri, int argCount) {
         mCallId = callId;
         mProcUri = procUri;
         mArgs = new Object[argCount];
      }
   }

   /**
    * RPC success response message.
    * Server-to-client message.
    */
   public static class CallResult {
      public String mCallId;
      public Object mResult;

      public CallResult(String callId, Object result) {
         mCallId = callId;
         mResult = result;
      }
   }

   /**
    * RPC failure response message.
    * Server-to-client message.
    */
   public static class CallError {
      public String mCallId;
      public String mErrorUri;
      public String mErrorDesc;

      public CallError(String callId, String errorUri, String errorDesc) {
         mCallId = callId;
         mErrorUri = errorUri;
         mErrorDesc = errorDesc;
      }
   }

   /**
    * Define CURIE message.
    * Server-to-client and client-to-server message.
    */
   public static class Prefix {
      public String mPrefix;
      public String mUri;

      public Prefix(String prefix, String uri) {
         mPrefix = prefix;
         mUri = uri;
      }
   }

   /**
    * Publish to topic URI request message.
    * Client-to-server message.
    */
   public static class Publish {
      public String mTopicUri;
      public Object mEvent;

      public Publish(String topicUri, Object event) {
         mTopicUri = topicUri;
         mEvent = event;
      }
   }

   /**
    * Subscribe to topic URI request message.
    * Client-to-server message.
    */
   public static class Subscribe {
      public String mTopicUri;

      public Subscribe(String topicUri) {
         mTopicUri = topicUri;
      }
   }

   /**
    * Unsubscribe from topic URI request message.
    * Client-to-server message.
    */
   public static class Unsubscribe {
      public String mTopicUri;

      public Unsubscribe(String topicUri) {
         mTopicUri = topicUri;
      }
   }

   /**
    * Event on topic URI message.
    * Server-to-client message.
    */
   public static class Event {
      public String mTopicUri;
      public Object mEvent;

      public Event(String topicUri, Object event) {
         mEvent = event;
      }
   }
}
