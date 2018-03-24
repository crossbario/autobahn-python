##############################################################################
##
# Crossbar.io Fabric ("Ueberschall")
# Copyright (C) Crossbar.io Technologies GmbH. All rights reserved.
##
##############################################################################

import sys
import time


def validate(validator, payload):
    """
    Simulates UTF8 validation in one go. In the actual WebSocket
    implementation within AutobahnPython, the validator is
    driven incrementally, as data arrives from the wire.
    """
    validator.reset()
    lastResult = validator.validate(payload)

    return

    if not lastResult[0]:
        raise Exception(
            "encountered invalid UTF-8 while processing text message at payload octet index %d" %
            lastResult[3])

    if not lastResult[1]:
        raise Exception(
            "UTF-8 text message payload ended within Unicode code point at payload octet index %d" %
            lastResult[3])


def fake_test_9_1_6(validator, payload, runs=1):
    """
    Fake the AutobahnTestsuite test 9.1.6

    http://autobahn.ws/testsuite/reports/servers/index.html
    https://github.com/tavendo/AutobahnTestSuite
    https://github.com/tavendo/AutobahnTestSuite/blob/master/autobahntestsuite/autobahntestsuite/case/case9_1_1.py
    https://github.com/tavendo/AutobahnTestSuite/blob/master/autobahntestsuite/autobahntestsuite/case/case9_1_6.py
    """
    for i in range(runs):
        # print "validating payload of length %d in one go" % len(payload)
        validate(validator, payload)


from autobahn.websocket.utf8validator import Utf8Validator
from test_cffi_validator import Utf8ValidatorCFFI


if __name__ == '__main__':

    VALIDATORS = []

    from cffi import FFI

    ffi = FFI()

    ffi.cdef("""
      typedef struct {
         size_t current_index;
         size_t total_index;
         int state;
         int is_valid;
         int ends_on_codepoint;
      } utf8_validator_t;

      void utf8vld_reset (utf8_validator_t* validator);

      void utf8vld_validate (utf8_validator_t* validator, const uint8_t* data, size_t length);
   """)

    ffi.validator = ffi.dlopen('libueberschall.so')

    validator = Utf8ValidatorCFFI(ffi)
    VALIDATORS.append(validator)

    validator = Utf8Validator()
    # VALIDATORS.append(validator)

    import random
    PAYLOAD = ''.join([random.choice(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") for i in xrange(16)])

    DATALEN = 16 * 2**20
    # not exactly, but good enough
    payload = PAYLOAD * (DATALEN / len(PAYLOAD))

    for validator in VALIDATORS:
        print("." * 80)
        print()
        print("using UTF8 validator", str(validator.__class__))
        print()

        runs = 200

        print("warming up ..")
        fake_test_9_1_6(validator, payload, runs)
        print()

        print("cooling down ..")
        time.sleep(3)
        print

        print("testing ..")
        t0 = time.time()
        fake_test_9_1_6(validator, payload, runs)
        t1 = time.time()
        totalBytes = float(runs * DATALEN)
        duration = t1 - t0
        print()
        print(
            "runtime %.4f s [%.1f MB/s]" %
            (duration, totalBytes / duration / 1024. / 1024.))
        print()
