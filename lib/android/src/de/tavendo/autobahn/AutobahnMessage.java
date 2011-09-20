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


public class AutobahnMessage {

   public static final int MESSAGE_TYPE_PREFIX = 1;
   public static final int MESSAGE_TYPE_CALL = 2;
   public static final int MESSAGE_TYPE_CALL_RESULT = 3;
   public static final int MESSAGE_TYPE_CALL_ERROR = 4;
   public static final int MESSAGE_TYPE_SUBSCRIBE = 5;
   public static final int MESSAGE_TYPE_UNSUBSCRIBE = 6;
   public static final int MESSAGE_TYPE_PUBLISH = 7;
   public static final int MESSAGE_TYPE_EVENT = 8;

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

   public static class CallResult {
      public String mCallId;
      public Object mResult;

      public CallResult(String callId, Object result) {
         mCallId = callId;
         mResult = result;
      }
   }

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
}
