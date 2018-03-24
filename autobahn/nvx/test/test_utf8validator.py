# coding=utf-8

###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from __future__ import absolute_import

import six

from autobahn.websocket.utf8validator import Utf8Validator


def _create_utf8_test_sequences():
    """
    Create test sequences for UTF-8 decoder tests from
    http://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt
    """

    UTF8_TEST_SEQUENCES = []

    # 1 Some correct UTF-8 text
    vss = b'\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5'
    vs = [b"Some valid UTF-8 sequences", []]
    vs[1].append((True, b'hello\x24world'))  # U+0024
    vs[1].append((True, b'hello\xC2\xA2world'))  # U+00A2
    vs[1].append((True, b'hello\xE2\x82\xACworld'))  # U+20AC
    vs[1].append((True, b'hello\xF0\xA4\xAD\xA2world'))  # U+24B62
    vs[1].append((True, vss))
    UTF8_TEST_SEQUENCES.append(vs)

    # All prefixes of correct UTF-8 text
    vs = [
        b"All prefixes of a valid UTF-8 string that contains multi-byte code points",
        []]
    v = Utf8Validator()
    for i in range(1, len(vss) + 1):
        v.reset()
        res = v.validate(vss[:i])
        vs[1].append((res[0] and res[1], vss[:i]))
    UTF8_TEST_SEQUENCES.append(vs)

    # 2.1 First possible sequence of a certain length
    vs = [b"First possible sequence of a certain length", []]
    vs[1].append((True, b'\x00'))
    vs[1].append((True, b'\xc2\x80'))
    vs[1].append((True, b'\xe0\xa0\x80'))
    vs[1].append((True, b'\xf0\x90\x80\x80'))
    UTF8_TEST_SEQUENCES.append(vs)

    # the following conform to the UTF-8 integer encoding scheme, but
    # valid UTF-8 only allows for Unicode code points up to U+10FFFF
    vs = [b"First possible sequence length 5/6 (invalid codepoints)", []]
    vs[1].append((False, b'\xf8\x88\x80\x80\x80'))
    vs[1].append((False, b'\xfc\x84\x80\x80\x80\x80'))
    UTF8_TEST_SEQUENCES.append(vs)

    # 2.2 Last possible sequence of a certain length
    vs = [b"Last possible sequence of a certain length", []]
    vs[1].append((True, b'\x7f'))
    vs[1].append((True, b'\xdf\xbf'))
    vs[1].append((True, b'\xef\xbf\xbf'))
    vs[1].append((True, b'\xf4\x8f\xbf\xbf'))
    UTF8_TEST_SEQUENCES.append(vs)

    # the following conform to the UTF-8 integer encoding scheme, but
    # valid UTF-8 only allows for Unicode code points up to U+10FFFF
    vs = [b"Last possible sequence length 4/5/6 (invalid codepoints)", []]
    vs[1].append((False, b'\xf7\xbf\xbf\xbf'))
    vs[1].append((False, b'\xfb\xbf\xbf\xbf\xbf'))
    vs[1].append((False, b'\xfd\xbf\xbf\xbf\xbf\xbf'))
    UTF8_TEST_SEQUENCES.append(vs)

    # 2.3 Other boundary conditions
    vs = [b"Other boundary conditions", []]
    vs[1].append((True, b'\xed\x9f\xbf'))
    vs[1].append((True, b'\xee\x80\x80'))
    vs[1].append((True, b'\xef\xbf\xbd'))
    vs[1].append((True, b'\xf4\x8f\xbf\xbf'))
    vs[1].append((False, b'\xf4\x90\x80\x80'))
    UTF8_TEST_SEQUENCES.append(vs)

    # 3.1  Unexpected continuation bytes
    vs = [b"Unexpected continuation bytes", []]
    vs[1].append((False, b'\x80'))
    vs[1].append((False, b'\xbf'))
    vs[1].append((False, b'\x80\xbf'))
    vs[1].append((False, b'\x80\xbf\x80'))
    vs[1].append((False, b'\x80\xbf\x80\xbf'))
    vs[1].append((False, b'\x80\xbf\x80\xbf\x80'))
    vs[1].append((False, b'\x80\xbf\x80\xbf\x80\xbf'))
    s = b""

    # 3.2  Lonely start characters
    vs = [b"Lonely start characters", []]
    m = [(0xc0, 0xdf), (0xe0, 0xef), (0xf0, 0xf7), (0xf8, 0xfb), (0xfc, 0xfd)]
    for mm in m:
        s = ''
        for i in range(mm[0], mm[1]):
            s += chr(i)
            s += chr(0x20)
        vs[1].append((False, s))
    UTF8_TEST_SEQUENCES.append(vs)

    # 3.3  Sequences with last continuation byte missing
    vs = [b"Sequences with last continuation byte missing", []]
    k = [b'\xc0', b'\xe0\x80', b'\xf0\x80\x80', b'\xf8\x80\x80\x80', b'\xfc\x80\x80\x80\x80',
         b'\xdf', b'\xef\xbf', b'\xf7\xbf\xbf', b'\xfb\xbf\xbf\xbf', b'\xfd\xbf\xbf\xbf\xbf']
    for kk in k:
        vs[1].append((False, kk))
    UTF8_TEST_SEQUENCES.append(vs)

    # 3.4  Concatenation of incomplete sequences
    vs = [b"Concatenation of incomplete sequences", []]
    vs[1].append((False, b''.join(k)))
    UTF8_TEST_SEQUENCES.append(vs)

    # 3.5  Impossible bytes
    vs = [b"Impossible bytes", []]
    vs[1].append((False, b'\xfe'))
    vs[1].append((False, b'\xff'))
    vs[1].append((False, b'\xfe\xfe\xff\xff'))
    UTF8_TEST_SEQUENCES.append(vs)

    # 4.1  Examples of an overlong ASCII character
    vs = [b"Examples of an overlong ASCII character", []]
    vs[1].append((False, b'\xc0\xaf'))
    vs[1].append((False, b'\xe0\x80\xaf'))
    vs[1].append((False, b'\xf0\x80\x80\xaf'))
    vs[1].append((False, b'\xf8\x80\x80\x80\xaf'))
    vs[1].append((False, b'\xfc\x80\x80\x80\x80\xaf'))
    UTF8_TEST_SEQUENCES.append(vs)

    # 4.2  Maximum overlong sequences
    vs = [b"Maximum overlong sequences", []]
    vs[1].append((False, b'\xc1\xbf'))
    vs[1].append((False, b'\xe0\x9f\xbf'))
    vs[1].append((False, b'\xf0\x8f\xbf\xbf'))
    vs[1].append((False, b'\xf8\x87\xbf\xbf\xbf'))
    vs[1].append((False, b'\xfc\x83\xbf\xbf\xbf\xbf'))
    UTF8_TEST_SEQUENCES.append(vs)

    # 4.3  Overlong representation of the NUL character
    vs = [b"Overlong representation of the NUL character", []]
    vs[1].append((False, b'\xc0\x80'))
    vs[1].append((False, b'\xe0\x80\x80'))
    vs[1].append((False, b'\xf0\x80\x80\x80'))
    vs[1].append((False, b'\xf8\x80\x80\x80\x80'))
    vs[1].append((False, b'\xfc\x80\x80\x80\x80\x80'))
    UTF8_TEST_SEQUENCES.append(vs)

    # 5.1 Single UTF-16 surrogates
    vs = [b"Single UTF-16 surrogates", []]
    vs[1].append((False, b'\xed\xa0\x80'))
    vs[1].append((False, b'\xed\xad\xbf'))
    vs[1].append((False, b'\xed\xae\x80'))
    vs[1].append((False, b'\xed\xaf\xbf'))
    vs[1].append((False, b'\xed\xb0\x80'))
    vs[1].append((False, b'\xed\xbe\x80'))
    vs[1].append((False, b'\xed\xbf\xbf'))
    UTF8_TEST_SEQUENCES.append(vs)

    # 5.2 Paired UTF-16 surrogates
    vs = [b"Paired UTF-16 surrogates", []]
    vs[1].append((False, b'\xed\xa0\x80\xed\xb0\x80'))
    vs[1].append((False, b'\xed\xa0\x80\xed\xbf\xbf'))
    vs[1].append((False, b'\xed\xad\xbf\xed\xb0\x80'))
    vs[1].append((False, b'\xed\xad\xbf\xed\xbf\xbf'))
    vs[1].append((False, b'\xed\xae\x80\xed\xb0\x80'))
    vs[1].append((False, b'\xed\xae\x80\xed\xbf\xbf'))
    vs[1].append((False, b'\xed\xaf\xbf\xed\xb0\x80'))
    vs[1].append((False, b'\xed\xaf\xbf\xed\xbf\xbf'))
    UTF8_TEST_SEQUENCES.append(vs)

    # 5.3 Other illegal code positions
    # Those are non-character code points and valid UTF-8 by RFC 3629
    vs = [b"Non-character code points (valid UTF-8)", []]
    # https://bug686312.bugzilla.mozilla.org/attachment.cgi?id=561257
    # non-characters: EF BF [BE-BF]
    vs[1].append((True, b'\xef\xbf\xbe'))
    vs[1].append((True, b'\xef\xbf\xbf'))
    # non-characters: F[0-7] [89AB]F BF [BE-BF]
    for z1 in [b'\xf0', b'\xf1', b'\xf2', b'\xf3', b'\xf4']:
        for z2 in [b'\x8f', b'\x9f', b'\xaf', b'\xbf']:
            if not (z1 == b'\xf4' and z2 !=
                    b'\x8f'):  # those encode codepoints >U+10FFFF
                for z3 in [b'\xbe', b'\xbf']:
                    zz = z1 + z2 + b'\xbf' + z3
                    if zz not in [b'\xf0\x8f\xbf\xbe',
                                  b'\xf0\x8f\xbf\xbf']:  # filter overlong sequences
                        vs[1].append((True, zz))
    UTF8_TEST_SEQUENCES.append(vs)

    # Unicode "specials", such as replacement char etc
    # http://en.wikipedia.org/wiki/Specials_%28Unicode_block%29
    vs = [b"Unicode specials (i.e. replacement char)", []]
    vs[1].append((True, b'\xef\xbf\xb9'))
    vs[1].append((True, b'\xef\xbf\xba'))
    vs[1].append((True, b'\xef\xbf\xbb'))
    vs[1].append((True, b'\xef\xbf\xbc'))
    vs[1].append((True, b'\xef\xbf\xbd'))  # replacement char
    vs[1].append((True, b'\xef\xbf\xbe'))
    vs[1].append((True, b'\xef\xbf\xbf'))
    UTF8_TEST_SEQUENCES.append(vs)

    return UTF8_TEST_SEQUENCES


def _create_valid_utf8_test_sequences():
    """
    Generate some exotic, but valid UTF8 test strings.
    """
    VALID_UTF8_TEST_SEQUENCES = []
    for test in create_utf8_test_sequences():
        valids = [x[1] for x in test[1] if x[0]]
        if len(valids) > 0:
            VALID_UTF8_TEST_SEQUENCES.append([test[0], valids])
    return VALID_UTF8_TEST_SEQUENCES


def _test_utf8(validator):
    """
    These tests verify the UTF-8 decoder/validator on the various test cases from
    http://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt
    """
    vs = []
    for k in create_utf8_test_sequences():
        vs.extend(k[1])

    # All Unicode code points
    for i in range(
            0, 0xffff):  # should by 0x10ffff, but non-wide Python build is limited to 16-bits
        if i < 0xD800 or i > 0xDFFF:  # filter surrogate code points, which are disallowed to encode in UTF-8
            vs.append((True, six.unichr(i).encode("utf-8")))

    # 5.1 Single UTF-16 surrogates
    for i in range(0xD800, 0xDBFF):  # high-surrogate
        ss = six.unichr(i).encode("utf-8")
        vs.append((False, ss))
    for i in range(0xDC00, 0xDFFF):  # low-surrogate
        ss = six.unichr(i).encode("utf-8")
        vs.append((False, ss))

    # 5.2 Paired UTF-16 surrogates
    for i in range(0xD800, 0xDBFF):  # high-surrogate
        for j in range(0xDC00, 0xDFFF):  # low-surrogate
            ss1 = six.unichr(i).encode("utf-8")
            ss2 = six.unichr(j).encode("utf-8")
            vs.append((False, ss1 + ss2))
            vs.append((False, ss2 + ss1))

    print("testing validator %s on %d UTF8 sequences" % (validator, len(vs)))

    # now test and assert ..
    for s in vs:
        validator.reset()
        r = validator.validate(s[1])
        res = r[0] and r[1]  # no UTF-8 decode error and everything consumed
        assert res == s[0]

    print("ok, validator works!")
    print("")


def _test_utf8_incremental(validator, withPositions=True):
    """
    These tests verify that the UTF-8 decoder/validator can operate incrementally.
    """
    if withPositions:
        k = 4
        print(
            "testing validator %s on incremental detection with positions" %
            validator)
    else:
        k = 2
        print(
            "testing validator %s on incremental detection without positions" %
            validator)

    validator.reset()
    assert (True, True, 15, 15)[:k] == validator.validate("µ@ßöäüàá")[:k]

    validator.reset()
    assert (False, False, 0, 0)[:k] == validator.validate("\xF5")[:k]

    # the following 3 all fail on eating byte 7 (0xA0)
    validator.reset()
    assert (True, True, 6, 6)[:k] == validator.validate(
        "\x65\x64\x69\x74\x65\x64")[:k]
    assert (False, False, 1, 7)[:k] == validator.validate("\xED\xA0\x80")[:k]

    validator.reset()
    assert (True, True, 4, 4)[:k] == validator.validate("\x65\x64\x69\x74")[:k]
    assert (
        False, False, 3, 7)[
        :k] == validator.validate("\x65\x64\xED\xA0\x80")[
            :k]

    validator.reset()
    assert (True, False, 7, 7)[:k] == validator.validate(
        "\x65\x64\x69\x74\x65\x64\xED")[:k]
    assert (False, False, 0, 7)[:k] == validator.validate("\xA0\x80")[:k]

    print("ok, validator works!")
    print("")
