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
import java.io.InputStream;
import java.nio.ByteBuffer;

public class ByteBufferInputStream extends InputStream {

   private final ByteBuffer mBuffer;

   public ByteBufferInputStream(ByteBuffer buffer) {
      mBuffer = buffer;
   }

   @Override
   public synchronized int read() throws IOException {

      if (!mBuffer.hasRemaining()) {
         return -1;
      } else {
         return mBuffer.get() & 0xFF;
      }
   }

   @Override
   public synchronized int read(byte[] bytes, int off, int len)
         throws IOException {

      if (bytes == null) {
         throw new NullPointerException();
      } else if (off < 0 || len < 0 || len > bytes.length - off) {
         throw new IndexOutOfBoundsException();
      } else if (len == 0) {
         return 0;
      }

      int length = Math.min(mBuffer.remaining(), len);
      if (length == 0) {
         return -1;
      }

      mBuffer.get(bytes, off, length);
      return length;
   }

}
