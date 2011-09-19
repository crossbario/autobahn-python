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

public class WebSocketOptions {

   private int mMaxFramePayloadSize = 4 * 1024 * 1024;
   private int mMaxMessagePayloadSize = 4 * 1024 * 1024;
   private boolean mReceiveTextMessagesRaw = false;
   private boolean mTcpNoDelay = true;
   private int mSocketReceiveTimeout = 200;
   private boolean mValidateIncomingUtf8 = true;
   private boolean mMaskClientFrames = true;

   public WebSocketOptions() {
   }

   public WebSocketOptions(WebSocketOptions other) {
      mMaxFramePayloadSize = other.mMaxFramePayloadSize;
      mMaxMessagePayloadSize = other.mMaxMessagePayloadSize;
      mReceiveTextMessagesRaw = other.mReceiveTextMessagesRaw;
      mTcpNoDelay = other.mTcpNoDelay;
      mSocketReceiveTimeout = other.mSocketReceiveTimeout;
      mValidateIncomingUtf8 = other.mValidateIncomingUtf8;
      mMaskClientFrames = other.mMaskClientFrames;
   }

   public void setReceiveTextMessagesRaw(boolean enabled) {
      mReceiveTextMessagesRaw = enabled;
   }

   public boolean getReceiveTextMessagesRaw() {
      return mReceiveTextMessagesRaw;
   }

   public void setMaxFramePayloadSize(int size) {
      if (size > 0) {
         mMaxFramePayloadSize = size;
      }
   }

   public int getMaxFramePayloadSize() {
      return mMaxFramePayloadSize;
   }

   public void setMaxMessagePayloadSize(int size) {
      if (size >= mMaxFramePayloadSize) {
         mMaxMessagePayloadSize = size;
      }
   }

   public int getMaxMessagePayloadSize() {
      return mMaxMessagePayloadSize;
   }

   public void setTcpNoDelay(boolean enabled) {
      mTcpNoDelay = enabled;
   }

   public boolean getTcpNoDelay() {
      return mTcpNoDelay;
   }

   public void setSocketReceiveTimeout(int timeoutMs) {
      if (timeoutMs >= 0) {
         mSocketReceiveTimeout = timeoutMs;
      }
   }

   public int getSocketReceiveTimeout() {
      return mSocketReceiveTimeout;
   }

   public void setValidateIncomingUtf8(boolean enabled) {
      mValidateIncomingUtf8 = enabled;
   }

   public boolean getValidateIncomingUtf8() {
      return mValidateIncomingUtf8;
   }

   public void setMaskClientFrames(boolean enabled) {
      mMaskClientFrames = enabled;
   }

   public boolean getMaskClientFrames() {
      return mMaskClientFrames;
   }
}
