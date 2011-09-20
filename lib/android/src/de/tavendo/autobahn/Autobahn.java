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


import org.codehaus.jackson.type.TypeReference;

public interface Autobahn {

   public interface OnSession {

      public static final int CLOSE_NORMAL = 1;
      public static final int CLOSE_CANNOT_CONNECT = 2;
      public static final int CLOSE_CONNECTION_LOST = 3;
      public static final int CLOSE_PROTOCOL_ERROR = 4;

      public void onOpen();

      public void onClose(int code, String reason);

   }

   public void connect(String wsUri, OnSession sessionHandler);

   public interface OnCallResult {

      public void onResult(Object result);

      public void onError(String errorId, String errorInfo);
   }

   public void call(String procedureId, Class<?> resultType, OnCallResult resultHandler, Object... arguments);

   public void call(String procedureId, TypeReference<?> resultType, OnCallResult resultHandler, Object... arguments);

   /*
    * Wire format for calls.
    *
    * Call (client-to-server JSON message):
    *
    *    ["call", <callId>, <procedureId>, <argument>]
    *
    * Result (server-to-client JSON message):
    *
    *    ["callresult", <callId>, <result>]
    *
    * Error (server-to-client JSON message):
    *
    *    ["callerror", <callId>, <errorId>, <errorInfo>]
    */


/*
   public interface OnEventListener {

      //public void onSubscribeSuccess();

      //public void onSubscribeError(String errorId, String errorInfo);

      public void onEvent(Object event);

      //public void onUnsubscribe();
   }
   public void subscribe(String eventId, Class<?> eventType, OnEventListener eventListener);
*/

   /*
   public void subscribe(String eventId, JavaType eventType, OnEventListener eventListener);

   public void subscribe(String eventId, Class<?> eventType, OnEventListener eventListener);

   public void subscribe(String eventId, TypeReference<?> eventType, OnEventListener eventListener);

   public void unsubscribe(String eventId, OnEventListener eventListener);

   public void unsubscribe(String eventId);

   public void unsubscribe();
   */
}
