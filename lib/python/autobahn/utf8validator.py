# coding=utf-8

###############################################################################
##
##  Copyright 2011 Tavendo GmbH
##
##  Note:
##
##  This code is a Python implementation of the algorithm
##
##            "Flexible and Economical UTF-8 Decoder"
##
##  by Bjoern Hoehrmann
##
##       bjoern@hoehrmann.de
##       http://bjoern.hoehrmann.de/utf-8/decoder/dfa/
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################


class Utf8Validator:
   """
   Incremental UTF-8 validator with constant memory consumption (minimal state).

   Implements the algorithm "Flexible and Economical UTF-8 Decoder" by
   Bjoern Hoehrmann (http://bjoern.hoehrmann.de/utf-8/decoder/dfa/).
   """

   ## DFA transitions
   UTF8VALIDATOR_DFA = [
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, # 00..1f
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, # 20..3f
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, # 40..5f
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, # 60..7f
     1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9, # 80..9f
     7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7, # a0..bf
     8,8,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2, # c0..df
     0xa,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x4,0x3,0x3, # e0..ef
     0xb,0x6,0x6,0x6,0x5,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8, # f0..ff
     0x0,0x1,0x2,0x3,0x5,0x8,0x7,0x1,0x1,0x1,0x4,0x6,0x1,0x1,0x1,0x1, # s0..s0
     1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,1, # s1..s2
     1,2,1,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1, # s3..s4
     1,2,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,3,1,1,1,1,1,1, # s5..s6
     1,3,1,1,1,1,1,3,1,3,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1, # s7..s8
   ]

   UTF8_ACCEPT = 0
   UTF8_REJECT = 1

   def __init__(self):
      self.reset()

   def decode(self, b):
      """
      Eat one UTF-8 octet, and validate on the fly.

      Returns UTF8_ACCEPT when enough octets have been consumed, in which case
      self.codepoint contains the decoded Unicode code point.

      Returns UTF8_REJECT when invalid UTF-8 was encountered.

      Returns some other positive integer when more octets need to be eaten.
      """
      type = Utf8Validator.UTF8VALIDATOR_DFA[b]
      if self.state != Utf8Validator.UTF8_ACCEPT:
         self.codepoint = (b & 0x3f) | (self.codepoint << 6)
      else:
         self.codepoint = (0xff >> type) & b
      self.state = Utf8Validator.UTF8VALIDATOR_DFA[256 + self.state * 16 + type]
      return self.state

   def reset(self):
      """
      Reset validator to start new incremental UTF-8 decode/validation.
      """
      self.state = Utf8Validator.UTF8_ACCEPT
      self.codepoint = 0
      self.i = 0

   def validate(self, ba):
      """
      Incrementally validate a chunk of bytes provided as bytearray.

      Will return a quad (valid?, endsOnCodePoint?, currentIndex, totalIndex).

      As soon as an octet is encountered which renders the octet sequence
      invalid, a quad with valid? == False is returned. currentIndex returns
      the index within the currently consumed chunk, and totalIndex the
      index within the total consumed sequence that was the point of bail out.
      When valid? == True, currentIndex will be len(ba) and totalIndex the
      total amount of consumed bytes.
      """
      l = len(ba)
      for i in xrange(0, l):
         ## optimized version of decode(), since we are not interested in actual code points
         self.state = Utf8Validator.UTF8VALIDATOR_DFA[256 + (self.state << 4) + Utf8Validator.UTF8VALIDATOR_DFA[ba[i]]]
         if self.state == Utf8Validator.UTF8_REJECT:
            self.i += i
            return False, False, i, self.i
      self.i += l
      return True, self.state == Utf8Validator.UTF8_ACCEPT, l, self.i


UTF8_TEST_SEQUENCES = []


def setTestSequences():
   """
   Setup test sequences for UTF-8 decoder tests from
   http://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt
   """

   # 1 Some correct UTF-8 text
   vss = '\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5'
   vs = ["Some valid UTF-8 sequences", []]
   vs[1].append((True, vss))
   UTF8_TEST_SEQUENCES.append(vs)

   # All prefixes of correct UTF-8 text
   vs = ["All prefixes of a valid UTF-8 string that contains multi-byte code points", []]
   v = Utf8Validator()
   for i in xrange(1, len(vss) + 1):
      v.reset()
      res = v.validate(bytearray(vss[:i]))
      vs[1].append((res[0] and res[1], vss[:i]))
   UTF8_TEST_SEQUENCES.append(vs)

   # 2.1 First possible sequence of a certain length
   vs = ["First possible sequence of a certain length", []]
   vs[1].append((True, '\x00'))
   vs[1].append((True, '\xc2\x80'))
   vs[1].append((True, '\xe0\xa0\x80'))
   vs[1].append((True, '\xf0\x90\x80\x80'))
   UTF8_TEST_SEQUENCES.append(vs)

   # the following conform to the UTF-8 integer encoding scheme, but
   # valid UTF-8 only allows for Unicode code points up to U+10FFFF
   vs = ["First possible sequence length 5/6 (invalid codepoints)", []]
   vs[1].append((False, '\xf8\x88\x80\x80\x80'))
   vs[1].append((False, '\xfc\x84\x80\x80\x80\x80'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 2.2 Last possible sequence of a certain length
   vs = ["Last possible sequence of a certain length", []]
   vs[1].append((True, '\x7f'))
   vs[1].append((True, '\xdf\xbf'))
   vs[1].append((True, '\xef\xbf\xbf'))
   vs[1].append((True, '\xf4\x8f\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # the following conform to the UTF-8 integer encoding scheme, but
   # valid UTF-8 only allows for Unicode code points up to U+10FFFF
   vs = ["Last possible sequence length 4/5/6 (invalid codepoints)", []]
   vs[1].append((False, '\xf7\xbf\xbf\xbf'))
   vs[1].append((False, '\xfb\xbf\xbf\xbf\xbf'))
   vs[1].append((False, '\xfd\xbf\xbf\xbf\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 2.3 Other boundary conditions
   vs = ["Other boundary conditions", []]
   vs[1].append((True, '\xed\x9f\xbf'))
   vs[1].append((True, '\xee\x80\x80'))
   vs[1].append((True, '\xef\xbf\xbd'))
   vs[1].append((True, '\xf4\x8f\xbf\xbf'))
   vs[1].append((False, '\xf4\x90\x80\x80'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 3.1  Unexpected continuation bytes
   vs = ["Unexpected continuation bytes", []]
   vs[1].append((False, '\x80'))
   vs[1].append((False, '\xbf'))
   vs[1].append((False, '\x80\xbf'))
   vs[1].append((False, '\x80\xbf\x80'))
   vs[1].append((False, '\x80\xbf\x80\xbf'))
   vs[1].append((False, '\x80\xbf\x80\xbf\x80'))
   vs[1].append((False, '\x80\xbf\x80\xbf\x80\xbf'))
   s = ""
   for i in xrange(0x80, 0xbf):
      s += chr(i)
   vs[1].append((False, s))
   UTF8_TEST_SEQUENCES.append(vs)

   # 3.2  Lonely start characters
   vs = ["Lonely start characters", []]
   m = [(0xc0, 0xdf), (0xe0, 0xef), (0xf0, 0xf7), (0xf8, 0xfb), (0xfc, 0xfd)]
   for mm in m:
      s = ''
      for i in xrange(mm[0], mm[1]):
         s += chr(i)
         s += chr(0x20)
      vs[1].append((False, s))
   UTF8_TEST_SEQUENCES.append(vs)

   # 3.3  Sequences with last continuation byte missing
   vs = ["Sequences with last continuation byte missing", []]
   k = ['\xc0', '\xe0\x80', '\xf0\x80\x80', '\xf8\x80\x80\x80', '\xfc\x80\x80\x80\x80',
        '\xdf', '\xef\xbf', '\xf7\xbf\xbf', '\xfb\xbf\xbf\xbf', '\xfd\xbf\xbf\xbf\xbf']
   for kk in k:
      vs[1].append((False, kk))
   UTF8_TEST_SEQUENCES.append(vs)

   # 3.4  Concatenation of incomplete sequences
   vs = ["Concatenation of incomplete sequences", []]
   vs[1].append((False, ''.join(k)))
   UTF8_TEST_SEQUENCES.append(vs)

   # 3.5  Impossible bytes
   vs = ["Impossible bytes", []]
   vs[1].append((False, '\xfe'))
   vs[1].append((False, '\xff'))
   vs[1].append((False, '\xfe\xfe\xff\xff'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 4.1  Examples of an overlong ASCII character
   vs = ["Examples of an overlong ASCII character", []]
   vs[1].append((False, '\xc0\xaf'))
   vs[1].append((False, '\xe0\x80\xaf'))
   vs[1].append((False, '\xf0\x80\x80\xaf'))
   vs[1].append((False, '\xf8\x80\x80\x80\xaf'))
   vs[1].append((False, '\xfc\x80\x80\x80\x80\xaf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 4.2  Maximum overlong sequences
   vs = ["Maximum overlong sequences", []]
   vs[1].append((False, '\xc1\xbf'))
   vs[1].append((False, '\xe0\x9f\xbf'))
   vs[1].append((False, '\xf0\x8f\xbf\xbf'))
   vs[1].append((False, '\xf8\x87\xbf\xbf\xbf'))
   vs[1].append((False, '\xfc\x83\xbf\xbf\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 4.3  Overlong representation of the NUL character
   vs = ["Overlong representation of the NUL character", []]
   vs[1].append((False, '\xc0\x80'))
   vs[1].append((False, '\xe0\x80\x80'))
   vs[1].append((False, '\xf0\x80\x80\x80'))
   vs[1].append((False, '\xf8\x80\x80\x80\x80'))
   vs[1].append((False, '\xfc\x80\x80\x80\x80\x80'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 5.1 Single UTF-16 surrogates
   vs = ["Single UTF-16 surrogates", []]
   vs[1].append((False, '\xed\xa0\x80'))
   vs[1].append((False, '\xed\xad\xbf'))
   vs[1].append((False, '\xed\xae\x80'))
   vs[1].append((False, '\xed\xaf\xbf'))
   vs[1].append((False, '\xed\xb0\x80'))
   vs[1].append((False, '\xed\xbe\x80'))
   vs[1].append((False, '\xed\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 5.2 Paired UTF-16 surrogates
   vs = ["Paired UTF-16 surrogates", []]
   vs[1].append((False, '\xed\xa0\x80\xed\xb0\x80'))
   vs[1].append((False, '\xed\xa0\x80\xed\xbf\xbf'))
   vs[1].append((False, '\xed\xad\xbf\xed\xb0\x80'))
   vs[1].append((False, '\xed\xad\xbf\xed\xbf\xbf'))
   vs[1].append((False, '\xed\xae\x80\xed\xb0\x80'))
   vs[1].append((False, '\xed\xae\x80\xed\xbf\xbf'))
   vs[1].append((False, '\xed\xaf\xbf\xed\xb0\x80'))
   vs[1].append((False, '\xed\xaf\xbf\xed\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 5.3 Other illegal code positions
   # Those are non-character code points and valid UTF-8 by RFC 3629
   vs = ["Non-character code points (valid UTF-8)", []]
   vs[1].append((True, '\xef\xbf\xbe'))
   vs[1].append((True, '\xef\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # Unicode replacement character
   vs = ["Unicode replacement character", []]
   vs[1].append((True, '\xef\xbf\xbd'))
   UTF8_TEST_SEQUENCES.append(vs)


setTestSequences()


def test_utf8():
   """
   These tests verify the UTF-8 decoder/validator on the various test cases from
   http://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt
   """

   v = Utf8Validator()
   vs = []
   for k in UTF8_TEST_SEQUENCES:
      vs.extend(k[1])

   # All Unicode code points
   for i in xrange(0, 0xffff): # should by 0x10ffff, but non-wide Python build is limited to 16-bits
      if i < 0xD800 or i > 0xDFFF: # filter surrogate code points, which are disallowed to encode in UTF-8
         vs.append((True, unichr(i).encode("utf-8")))

   # 5.1 Single UTF-16 surrogates
   for i in xrange(0xD800, 0xDBFF): # high-surrogate
      ss = unichr(i).encode("utf-8")
      vs.append((False, ss))
   for i in xrange(0xDC00, 0xDFFF): # low-surrogate
      ss = unichr(i).encode("utf-8")
      vs.append((False, ss))

   # 5.2 Paired UTF-16 surrogates
   for i in xrange(0xD800, 0xDBFF): # high-surrogate
      for j in xrange(0xDC00, 0xDFFF): # low-surrogate
         ss1 = unichr(i).encode("utf-8")
         ss2 = unichr(j).encode("utf-8")
         vs.append((False, ss1 + ss2))
         vs.append((False, ss2 + ss1))

   # now test and assert ..
   for s in vs:
      v.reset()
      r = v.validate(bytearray(s[1]))
      res = r[0] and r[1] # no UTF-8 decode error and everything consumed
      assert res == s[0]


def test_utf8_incremental():
   """
   These tests verify that the UTF-8 decoder/validator can operate incrementally.
   """

   v = Utf8Validator()

   v.reset()
   assert (True, True, 15, 15) == v.validate(bytearray("µ@ßöäüàá"))

   v.reset()
   assert (False, False, 0, 0) == v.validate(bytearray([0xF5]))

   ## the following 3 all fail on eating byte 7 (0xA0)
   v.reset()
   assert (True, True, 6, 6) == v.validate(bytearray([0x65, 0x64, 0x69, 0x74, 0x65, 0x64]))
   assert (False, False, 1, 7) == v.validate(bytearray([0xED, 0xA0, 0x80]))

   v.reset()
   assert (True, True, 4, 4) == v.validate(bytearray([0x65, 0x64, 0x69, 0x74]))
   assert (False, False, 3, 7) == v.validate(bytearray([0x65, 0x64, 0xED, 0xA0, 0x80]))

   v.reset()
   assert (True, False, 7, 7) == v.validate(bytearray([0x65, 0x64, 0x69, 0x74, 0x65, 0x64, 0xED]))
   assert (False, False, 0, 7) == v.validate(bytearray([0xA0, 0x80]))


if __name__ == '__main__':
   """
   Run unit tests.
   """
   test_utf8_incremental()
   test_utf8()
