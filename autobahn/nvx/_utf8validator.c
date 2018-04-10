///////////////////////////////////////////////////////////////////////////////
//
// The MIT License (MIT)
//
// Copyright (c) Crossbar.io Technologies GmbH
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//
///////////////////////////////////////////////////////////////////////////////

#include <stdlib.h>
#include <stdint.h>

// http://stackoverflow.com/questions/11228855/header-files-for-simd-intrinsics
#include <x86intrin.h>


#define UTF8_ACCEPT 0
#define UTF8_REJECT 1


typedef struct {
   size_t   current_index;
   size_t   total_index;
   int      state;
   int      impl;
} utf8_validator_t;


#define UTF8_VALIDATOR_OPTIMAL 0
#define UTF8_VALIDATOR_TABLE_DFA 1
#define UTF8_VALIDATOR_UNROLLED_DFA 2
#define UTF8_VALIDATOR_SSE2_DFA 3
#define UTF8_VALIDATOR_SSE41_DFA 4


int nvx_utf8vld_get_impl (void* utf8vld) {
   utf8_validator_t* vld = (utf8_validator_t*) utf8vld;

   return vld->impl;
}

int nvx_utf8vld_set_impl (void* utf8vld, int impl) {
   utf8_validator_t* vld = (utf8_validator_t*) utf8vld;

   if (impl) {
      // set requested implementation
      //
#ifndef __SSE4_1__
#  ifdef __SSE2__
      if (impl <= UTF8_VALIDATOR_SSE2_DFA) {
         vld->impl = impl;
      }
#  else
      if (impl <= UTF8_VALIDATOR_UNROLLED_DFA) {
         vld->impl = impl;
      }
#  endif
#else
      if (impl <= UTF8_VALIDATOR_SSE41_DFA) {
         vld->impl = impl;
      }
#endif

   } else {
      // set optimal implementation
      //
#ifndef __SSE4_1__
#  ifdef __SSE2__
      vld->impl = UTF8_VALIDATOR_SSE2_DFA;
#  else
      vld->impl = UTF8_VALIDATOR_UNROLLED_DFA;
#  endif
#else
      vld->impl = UTF8_VALIDATOR_SSE41_DFA;
#endif

   }
   return vld->impl;
}


void nvx_utf8vld_reset (void* utf8vld) {
   utf8_validator_t* vld = (utf8_validator_t*) utf8vld;

   vld->state = 0;
   vld->current_index = -1;
   vld->total_index = -1;
}


void* nvx_utf8vld_new () {
   void* p = malloc(sizeof(utf8_validator_t));
   nvx_utf8vld_reset(p);
   nvx_utf8vld_set_impl(p, 0);
   return p;
}


void nvx_utf8vld_free (void* utf8vld) {
   free (utf8vld);
}


// unrolled DFA from http://bjoern.hoehrmann.de/utf-8/decoder/dfa/
//
static const uint8_t UTF8VALIDATOR_DFA[] __attribute__((aligned(64))) =
{
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


int _nvx_utf8vld_validate_table (void* utf8vld, const uint8_t* data, size_t length) {

   utf8_validator_t* vld = (utf8_validator_t*) utf8vld;

   int state = vld->state;

   const uint8_t* end = data + length;

   while (data < end && state != 1) {
      state = UTF8VALIDATOR_DFA[256 + state * 16 + UTF8VALIDATOR_DFA[*data++]];
   }

   vld->state = state;

   if (state == 0) {
      // UTF8 is valid and ends on codepoint
      return 0;
   } else {
      if (state == 1) {
         // UTF8 is invalid
         return -1;
      } else {
         // UTF8 is valid, but does not end on codepoint (needs more data)
         return 1;
      }
   }
}


// unrolled DFA from http://bjoern.hoehrmann.de/utf-8/decoder/dfa/
//
#define DFA_TRANSITION(state, octet) \
   if (state == 0) { \
      if (octet >= 0x00 && octet <= 0x7f) { \
         /* reflective state 0 */ \
      } else if (octet >= 0xc2 && octet <= 0xdf) { \
         state = 2; \
      } else if ((octet >= 0xe1 && octet <= 0xec) || octet == 0xee || octet == 0xef) { \
         state = 3; \
      } else if (octet == 0xe0) { \
         state = 4; \
      } else if (octet == 0xed) { \
         state = 5; \
      } else if (octet == 0xf4) { \
         state = 8; \
      } else if (octet == 0xf1 || octet == 0xf2 || octet == 0xf3) { \
         state = 7; \
      } else if (octet == 0xf0) { \
         state = 6; \
      } else { \
         state = 1; \
      } \
   } else if (state == 2) { \
      if (octet >= 0x80 && octet <= 0xbf) { \
         state = 0; \
      } else { \
         state = 1; \
      } \
   } else if (state == 3) { \
      if (octet >= 0x80 && octet <= 0xbf) { \
         state = 2; \
      } else { \
         state = 1; \
      } \
   } else if (state == 4) { \
      if (octet >= 0xa0 && octet <= 0xbf) { \
         state = 2; \
      } else { \
         state = 1; \
      } \
   } else if (state == 5) { \
      if (octet >= 0x80 && octet <= 0x9f) { \
         state = 2; \
      } else { \
         state = 1; \
      } \
   } else if (state == 6) { \
      if (octet >= 0x90 && octet <= 0xbf) { \
         state = 3; \
      } else { \
         state = 1; \
      } \
   } else if (state == 7) { \
      if (octet >= 0x80 && octet <= 0xbf) { \
         state = 3; \
      } else { \
         state = 1; \
      } \
   } else if (state == 8) { \
      if (octet >= 0x80 && octet <= 0x8f) { \
         state = 3; \
      } else { \
         state = 1; \
      } \
   } else if (state == 1) { \
      /* refective state 1 */ \
   } else { \
      /* should not arrive here */ \
   }


int _nvx_utf8vld_validate_unrolled (void* utf8vld, const uint8_t* data, size_t length) {

   utf8_validator_t* vld = (utf8_validator_t*) utf8vld;

   int state = vld->state;

   const uint8_t* tail_end = data + length;

   while (data < tail_end && state != 1) {

      // get tail octet
      int octet = *data;

      // do the DFA
      DFA_TRANSITION(state, octet);

      ++data;
   }

   vld->state = state;

   if (state == 0) {
      // UTF8 is valid and ends on codepoint
      return 0;
   } else {
      if (state == 1) {
         // UTF8 is invalid
         return -1;
      } else {
         // UTF8 is valid, but does not end on codepoint (needs more data)
         return 1;
      }
   }
}


/*
   __m128i _mm_load_si128 (__m128i const* mem_addr)
      #include "emmintrin.h"
      Instruction: movdqa
      CPUID Feature Flag: SSE2

   int _mm_movemask_epi8 (__m128i a)
      #include "emmintrin.h"
      Instruction: pmovmskb
      CPUID Feature Flag: SSE2

   __m128i _mm_srli_si128 (__m128i a, int imm)
      #include "emmintrin.h"
      Instruction: psrldq
      CPUID Feature Flag: SSE2

   int _mm_cvtsi128_si32 (__m128i a)
      #include "emmintrin.h"
      Instruction: movd
      CPUID Feature Flag: SSE2

   int _mm_extract_epi16 (__m128i a, int imm)
      #include "emmintrin.h"
      Instruction: pextrw
      CPUID Feature Flag: SSE2

   int _mm_extract_epi8 (__m128i a, const int imm)
      #include "smmintrin.h"
      Instruction: pextrb
      CPUID Feature Flag: SSE4.1
*/

#ifdef __SSE2__
int _nvx_utf8vld_validate_sse2 (void* utf8vld, const uint8_t* data, size_t length) {

   utf8_validator_t* vld = (utf8_validator_t*) utf8vld;

   int state = vld->state;

   const uint8_t* tail_end = data + length;

   // process unaligned head (sub 16 octets)
   //
   size_t head_len = ((size_t) data) % sizeof(__m128i);
   if (head_len) {

      const uint8_t* head_end = data + head_len;

      while (data < head_end && state != UTF8_REJECT) {

         // get head octet
         int octet = *data;

         // do the DFA
         DFA_TRANSITION(state, octet);

         ++data;
      }
   }

   // process aligned middle (16 octet chunks)
   //
   const __m128i* ptr = ((const __m128i*) data);
   const __m128i* end = ((const __m128i*) data) + ((length - head_len) / sizeof(__m128i));

   while (ptr < end && state != UTF8_REJECT) {

      __builtin_prefetch(ptr + 1, 0, 3);
      //__builtin_prefetch(ptr + 4, 0, 3); // 16*4=64: cache-line prefetch

      __m128i xmm1 = _mm_load_si128(ptr);

      if (__builtin_expect(state || _mm_movemask_epi8(xmm1), 0)) {

         // copy to different reg - this allows the prefetching to
         // do its job in the meantime (I guess ..)

         // SSE2 variant
         //
         int octet;

         // octet 0
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 1
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 2
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 3
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 4
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 5
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 6
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 7
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 8
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 9
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 10
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 11
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 12
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 13
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 14
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);

         // octet 15
         xmm1 = _mm_srli_si128(xmm1,  1);
         octet = 0xff & _mm_cvtsi128_si32(xmm1);
         DFA_TRANSITION(state, octet);
      }
      ++ptr;
   }

   // process unaligned tail (sub 16 octets)
   //
   const uint8_t* tail_ptr = (const uint8_t*) ptr;

   while (tail_ptr < tail_end && state != UTF8_REJECT) {

      // get tail octet
      int octet = *tail_ptr;

      // do the DFA
      DFA_TRANSITION(state, octet);

      ++tail_ptr;
   }

   vld->state = state;

   if (state == UTF8_ACCEPT) {
      // UTF8 is valid and ends on codepoint
      return 0;
   } else {
      if (state == UTF8_REJECT) {
         // UTF8 is invalid
         return -1;
      } else {
         // UTF8 is valid, but does not end on codepoint (needs more data)
         return 1;
      }
   }
}
#endif


#ifdef __SSE4_1__
int _nvx_utf8vld_validate_sse4 (void* utf8vld, const uint8_t* data, size_t length) {

   utf8_validator_t* vld = (utf8_validator_t*) utf8vld;

   int state = vld->state;

   const uint8_t* tail_end = data + length;

   // process unaligned head (sub 16 octets)
   //
   size_t head_len = ((size_t) data) % sizeof(__m128i);
   if (head_len) {

      const uint8_t* head_end = data + head_len;

      while (data < head_end && state != UTF8_REJECT) {

         // get head octet
         int octet = *data;

         // do the DFA
         DFA_TRANSITION(state, octet);

         ++data;
      }
   }

   // process aligned middle (16 octet chunks)
   //
   const __m128i* ptr = ((const __m128i*) data);
   const __m128i* end = ((const __m128i*) data) + ((length - head_len) / sizeof(__m128i));

   while (ptr < end && state != UTF8_REJECT) {

      __builtin_prefetch(ptr + 1, 0, 3);
      //__builtin_prefetch(ptr + 4, 0, 3); // 16*4=64: cache-line prefetch

      __m128i xmm1 = _mm_load_si128(ptr);


      if (__builtin_expect(state || _mm_movemask_epi8(xmm1), 0)) {

         // copy to different reg - this allows the prefetching to
         // do its job in the meantime (I guess ..)

         // SSE4.1 variant
         //
         int octet;

         // octet 0
         octet = _mm_extract_epi8(xmm1, 0);
         DFA_TRANSITION(state, octet);

         // octet 1
         octet = _mm_extract_epi8(xmm1, 1);
         DFA_TRANSITION(state, octet);

         // octet 2
         octet = _mm_extract_epi8(xmm1, 2);
         DFA_TRANSITION(state, octet);

         // octet 3
         octet = _mm_extract_epi8(xmm1, 3);
         DFA_TRANSITION(state, octet);

         // octet 4
         octet = _mm_extract_epi8(xmm1, 4);
         DFA_TRANSITION(state, octet);

         // octet 5
         octet = _mm_extract_epi8(xmm1, 5);
         DFA_TRANSITION(state, octet);

         // octet 6
         octet = _mm_extract_epi8(xmm1, 6);
         DFA_TRANSITION(state, octet);

         // octet 7
         octet = _mm_extract_epi8(xmm1, 7);
         DFA_TRANSITION(state, octet);

         // octet 8
         octet = _mm_extract_epi8(xmm1, 8);
         DFA_TRANSITION(state, octet);

         // octet 9
         octet = _mm_extract_epi8(xmm1, 9);
         DFA_TRANSITION(state, octet);

         // octet 10
         octet = _mm_extract_epi8(xmm1, 10);
         DFA_TRANSITION(state, octet);

         // octet 11
         octet = _mm_extract_epi8(xmm1, 11);
         DFA_TRANSITION(state, octet);

         // octet 12
         octet = _mm_extract_epi8(xmm1, 12);
         DFA_TRANSITION(state, octet);

         // octet 13
         octet = _mm_extract_epi8(xmm1, 13);
         DFA_TRANSITION(state, octet);

         // octet 14
         octet = _mm_extract_epi8(xmm1, 14);
         DFA_TRANSITION(state, octet);

         // octet 15
         octet = _mm_extract_epi8(xmm1, 15);
         DFA_TRANSITION(state, octet);
      }
      ++ptr;
   }

   // process unaligned tail (sub 16 octets)
   //
   const uint8_t* tail_ptr = (const uint8_t*) ptr;

   while (tail_ptr < tail_end && state != UTF8_REJECT) {

      // get tail octet
      int octet = *tail_ptr;

      // do the DFA
      DFA_TRANSITION(state, octet);

      ++tail_ptr;
   }

   vld->state = state;

   if (state == UTF8_ACCEPT) {
      // UTF8 is valid and ends on codepoint
      return 0;
   } else {
      if (state == UTF8_REJECT) {
         // UTF8 is invalid
         return -1;
      } else {
         // UTF8 is valid, but does not end on codepoint (needs more data)
         return 1;
      }
   }
}
#endif


int nvx_utf8vld_validate (void* utf8vld, const uint8_t* data, size_t length) {

   utf8_validator_t* vld = (utf8_validator_t*) utf8vld;

   switch (vld->impl) {
      case UTF8_VALIDATOR_TABLE_DFA:
         return _nvx_utf8vld_validate_table(utf8vld, data, length);
      case UTF8_VALIDATOR_UNROLLED_DFA:
         return _nvx_utf8vld_validate_unrolled(utf8vld, data, length);
#ifdef __SSE2__
      case UTF8_VALIDATOR_SSE2_DFA:
         return _nvx_utf8vld_validate_table(utf8vld, data, length);
#endif
#ifdef __SSE4_1__
      case UTF8_VALIDATOR_SSE41_DFA:
         return _nvx_utf8vld_validate_table(utf8vld, data, length);
#endif
      default:
         return _nvx_utf8vld_validate_table(utf8vld, data, length);
   }
}
