///////////////////////////////////////////////////////////////////////////////
//
// The MIT License (MIT)
//
// Copyright (c) typedef int GmbH
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
#include <string.h>

// SIMD intrinsics
#if defined(__SSE2__)
#include <x86intrin.h>
#endif

typedef struct {
    uint8_t  mask[4];
    size_t   ptr;
    int      impl;
} xor_masker_t;

#define XOR_MASKER_OPTIMAL 0
#define XOR_MASKER_SIMPLE 1
#define XOR_MASKER_SSE2 2


int nvx_xormask_get_impl (void* xormask) {
    xor_masker_t* masker = (xor_masker_t*) xormask;
    return masker->impl;
}

int nvx_xormask_set_impl (void* xormask, int impl) {
    xor_masker_t* masker = (xor_masker_t*) xormask;

    if (impl) {
        // set requested implementation
#ifdef __SSE2__
        if (impl <= XOR_MASKER_SSE2) {
            masker->impl = impl;
        }
#else
        if (impl <= XOR_MASKER_SIMPLE) {
            masker->impl = impl;
        }
#endif
    } else {
        // set optimal implementation
#ifdef __SSE2__
        masker->impl = XOR_MASKER_SSE2;
#else
        masker->impl = XOR_MASKER_SIMPLE;
#endif
    }
    return masker->impl;
}

void nvx_xormask_reset (void* xormask) {
    xor_masker_t* masker = (xor_masker_t*) xormask;
    masker->ptr = 0;
}

size_t nvx_xormask_pointer (void* xormask) {
    xor_masker_t* masker = (xor_masker_t*) xormask;
    return masker->ptr;
}

void* nvx_xormask_new (const uint8_t* mask) {
    xor_masker_t* masker = (xor_masker_t*) malloc(sizeof(xor_masker_t));
    if (masker) {
        memcpy(masker->mask, mask, 4);
        masker->ptr = 0;
        nvx_xormask_set_impl(masker, 0);  // set optimal implementation
    }
    return masker;
}

void nvx_xormask_free (void* xormask) {
    free(xormask);
}


// Simple scalar implementation
void _nvx_xormask_process_simple (void* xormask, uint8_t* data, size_t length) {
    xor_masker_t* masker = (xor_masker_t*) xormask;
    size_t ptr = masker->ptr;

    for (size_t i = 0; i < length; i++) {
        data[i] ^= masker->mask[ptr & 3];
        ptr++;
    }

    masker->ptr = ptr;
}


#ifdef __SSE2__
// SSE2 SIMD implementation
void _nvx_xormask_process_sse2 (void* xormask, uint8_t* data, size_t length) {
    xor_masker_t* masker = (xor_masker_t*) xormask;
    size_t ptr = masker->ptr;

    // Build 16-byte mask pattern from 4-byte mask, accounting for starting position
    uint8_t mask16_bytes[16];
    for (int i = 0; i < 16; i++) {
        mask16_bytes[i] = masker->mask[(ptr + i) & 3];
    }
    __m128i xmm_mask = _mm_loadu_si128((__m128i*)mask16_bytes);

    size_t head_len = 0;

    // Process unaligned head (until 16-byte alignment)
    if (length >= 16) {
        head_len = ((uintptr_t)data) & 15;
        if (head_len) {
            head_len = 16 - head_len;
            if (head_len > length) head_len = length;

            for (size_t i = 0; i < head_len; i++) {
                data[i] ^= masker->mask[ptr & 3];
                ptr++;
            }

            data += head_len;
            length -= head_len;

            // Rebuild mask for aligned processing
            for (int i = 0; i < 16; i++) {
                mask16_bytes[i] = masker->mask[(ptr + i) & 3];
            }
            xmm_mask = _mm_loadu_si128((__m128i*)mask16_bytes);
        }
    }

    // Process aligned middle (16-byte chunks)
    __m128i* ptr128 = (__m128i*) data;
    size_t chunks = length / 16;

    for (size_t i = 0; i < chunks; i++) {
        __m128i xmm_data = _mm_load_si128(ptr128);
        xmm_data = _mm_xor_si128(xmm_data, xmm_mask);
        _mm_store_si128(ptr128, xmm_data);
        ptr128++;
    }

    ptr += chunks * 16;
    size_t processed = chunks * 16;

    // Process unaligned tail (remaining bytes)
    size_t tail_len = length - processed;
    if (tail_len) {
        uint8_t* tail_data = (uint8_t*)ptr128;
        for (size_t i = 0; i < tail_len; i++) {
            tail_data[i] ^= masker->mask[ptr & 3];
            ptr++;
        }
    }

    masker->ptr = ptr;
}
#endif


void nvx_xormask_process (void* xormask, uint8_t* data, size_t length) {
    xor_masker_t* masker = (xor_masker_t*) xormask;

    switch (masker->impl) {
        case XOR_MASKER_SIMPLE:
            _nvx_xormask_process_simple(xormask, data, length);
            break;
#ifdef __SSE2__
        case XOR_MASKER_SSE2:
            _nvx_xormask_process_sse2(xormask, data, length);
            break;
#endif
        default:
            _nvx_xormask_process_simple(xormask, data, length);
            break;
    }
}
