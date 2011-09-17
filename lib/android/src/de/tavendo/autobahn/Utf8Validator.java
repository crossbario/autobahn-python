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
 *  Incremental UTF-8 validator with constant memory consumption (minimal state).
 *
 *  Implements the algorithm "Flexible and Economical UTF-8 Decoder" by
 *  Bjoern Hoehrmann (http://bjoern.hoehrmann.de/utf-8/decoder/dfa/).
 */
public class Utf8Validator {

   /// DFA state transitions (14 x 32 = 448).
   private static final int[] DFA = {
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 00..1f
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 20..3f
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 40..5f
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 60..7f
      1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9, // 80..9f
      7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7, // a0..bf
      8,8,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2, // c0..df
      0xa,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x4,0x3,0x3, // e0..ef
      0xb,0x6,0x6,0x6,0x5,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8, // f0..ff
      0x0,0x1,0x2,0x3,0x5,0x8,0x7,0x1,0x1,0x1,0x4,0x6,0x1,0x1,0x1,0x1, // s0..s0
      1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,1, // s1..s2
      1,2,1,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1, // s3..s4
      1,2,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,3,1,1,1,1,1,1, // s5..s6
      1,3,1,1,1,1,1,3,1,3,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1  // s7..s8
   };

   private static final int ACCEPT = 0;
   private static final int REJECT = 1;

   private int mState;
   private int mPos;

   /**
    * Create new incremental UTF-8 validator. The validator is already
    * resetted and thus immediately usable.
    */
   public Utf8Validator() {
      reset();
   }

   /**
    * Reset validator state to begin validation of new
    * UTF-8 stream.
    */
   public void reset() {
      mState = ACCEPT;
      mPos = 0;
   }

   /**
    * Get end of validated position within stream. When validate()
    * returns false, indicating an UTF-8 error, this function can
    * be used to get the exact position within the stream upon
    * which the violation was encountered.
    *
    * @return     Current position with stream validated.
    */
   public int position() {
      return mPos;
   }

   /**
    * Check if incremental validation (currently) has ended on
    * a complete encoded Unicode codepoint.
    *
    * @return        True, iff currently ended on codepoint.
    */
   public boolean isValid() {
      return mState == ACCEPT;
   }

   /**
    * Validate a chunk of octets for UTF-8.
    *
    * @param data    Buffer which contains chunk to validate.
    * @param off     Offset within buffer where to continue with validation.
    * @param len     Length in octets to validate within buffer.
    * @return        False as soon as UTF-8 violation occurs, true otherwise.
    */
   public boolean validate(byte[] data, int off, int len) {
      for (int i = off; i < off + len; ++i) {
         mState = DFA[256 + (mState << 4) + DFA[(int) (0xff & data[i])]];
         if (mState == REJECT) {
            mPos += i;
            return false;
         }
      }
      mPos += len;
      return true;
   }

   /**
    * Validate a chunk of octets for UTF-8.
    *
    * @param data    Buffer which contains chunk to validate.
    * @return        False as soon as UTF-8 violation occurs, true otherwise.
    */
   public boolean validate(byte[] data) {
      return validate(data, 0, data.length);
   }

}
