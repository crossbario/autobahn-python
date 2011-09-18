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

import java.io.IOException;
import java.io.OutputStream;
import java.nio.Buffer;
import java.nio.ByteBuffer;

public class ByteBufferOutputStream extends OutputStream {

   @SuppressWarnings("unused")
   private static final String TAG = "de.tavendo.autobahn.ByteBufferOutputStream";

   private final int mInitialSize;
   private final int mGrowSize;
   private ByteBuffer mBuffer;

   public ByteBufferOutputStream() {
      this(2 * 65536, 65536);
   }

   public ByteBufferOutputStream(int initialSize, int growSize) {
      mInitialSize = initialSize;
      mGrowSize = growSize;
      mBuffer = ByteBuffer.allocateDirect(mInitialSize);
      mBuffer.clear();
   }

   public ByteBuffer getBuffer() {
      return mBuffer;
   }

   public Buffer flip() {
      return mBuffer.flip();
   }

   public Buffer clear() {
      return mBuffer.clear();
   }

   public int remaining() {
      return mBuffer.remaining();
   }

   public synchronized void expand(int requestSize) {

      if (requestSize > mBuffer.capacity()) {

         ByteBuffer oldBuffer = mBuffer;
         int oldPosition = mBuffer.position();
         int newCapacity = ((requestSize / mGrowSize) + 1) * mGrowSize;
         mBuffer = ByteBuffer.allocateDirect(newCapacity);
         oldBuffer.clear();
         mBuffer.clear();
         mBuffer.put(oldBuffer);
         mBuffer.position(oldPosition);
      }
   }

   @Override
   public synchronized void write(int b) throws IOException {

      if (mBuffer.position() + 1 > mBuffer.capacity()) {
         expand(mBuffer.capacity() + 1);
      }
      mBuffer.put((byte) b);
   }

   @Override
   public synchronized void write(byte[] bytes, int off, int len)
         throws IOException {

      if (mBuffer.position() + len > mBuffer.capacity()) {
         expand(mBuffer.capacity() + len);
      }
      mBuffer.put(bytes, off, len);
   }

   public synchronized void write(byte[] bytes) throws IOException {
      write(bytes, 0, bytes.length);
   }

   public synchronized void write(String str) throws IOException {
      write(str.getBytes("UTF-8"));
   }

   public synchronized void crlf() throws IOException {
      write(0x0d);
      write(0x0a);
   }

}

