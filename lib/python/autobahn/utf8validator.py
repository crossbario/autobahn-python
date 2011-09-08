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

import sys


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

      Will return a triple (valid?, currentIndex, totalIndex).

      As soon as an octet is encountered which renders the octet sequence
      invalid, a triple with valid? == False is returned. currentIndex returns
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
            return False, i, self.i
      self.i += l
      return True, l, self.i


if __name__ == '__main__':

   v = Utf8Validator()

   # http://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt

   vs = []

   # 1 Some correct UTF-8 text
   vs.append((True, '\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5'))

   # 2.1 First possible sequence of a certain length
   vs.append((True, '\x00'))
   vs.append((True, '\xc2\x80'))
   vs.append((True, '\xe0\xa0\x80'))
   vs.append((True, '\xf0\x90\x80\x80'))

   # the following conform to the UTF-8 integer encoding scheme, but
   # valid UTF-8 only allows for Unicode code points up to U+10FFFF
   vs.append((False, '\xf8\x88\x80\x80\x80'))
   vs.append((False, '\xfc\x84\x80\x80\x80\x80'))

   # 2.2 Last possible sequence of a certain length
   vs.append((True, '\x7f'))
   vs.append((True, '\xdf\xbf'))
   vs.append((True, '\xef\xbf\xbf'))
   vs.append((True, '\xf4\x8f\xbf\xbf'))

   # the following conform to the UTF-8 integer encoding scheme, but
   # valid UTF-8 only allows for Unicode code points up to U+10FFFF
   vs.append((False, '\xf7\xbf\xbf\xbf'))
   vs.append((False, '\xfb\xbf\xbf\xbf\xbf'))
   vs.append((False, '\xfd\xbf\xbf\xbf\xbf\xbf'))

   # 2.3 Other boundary conditions
   vs.append((True, '\xed\x9f\xbf'))
   vs.append((True, '\xee\x80\x80'))
   vs.append((False, '\xef\xbf\xbd'))
   vs.append((True, '\xf4\x8f\xbf\xbf'))
   vs.append((False, '\xf4\x90\x80\x80'))

   # 3.1  Unexpected continuation bytes
   vs.append((False, '\x80'))
   vs.append((False, '\xbf'))
   vs.append((False, '\x80\xbf'))
   vs.append((False, '\x80\xbf\x80'))
   vs.append((False, '\x80\xbf\x80\xbf'))
   vs.append((False, '\x80\xbf\x80\xbf\x80'))
   vs.append((False, '\x80\xbf\x80\xbf\x80\xbf'))
   s = ""
   for i in xrange(0x80, 0xbf):
      s += chr(i)
   vs.append((False, s))

   # 3.2  Lonely start characters
   m = [(0xc0, 0xdf), (0xe0, 0xef), (0xf0, 0xf7), (0xf8, 0xfb), (0xfc, 0xfd)]
   for mm in m:
      s = ''
      for i in xrange(mm[0], mm[1]):
         s += chr(i)
         s += chr(0x20)
      vs.append((False, s))

   # 3.3  Sequences with last continuation byte missing
   k = ['\xc0', '\xe0\x80', '\xf0\x80\x80', '\xf8\x80\x80\x80', '\xfc\x80\x80\x80\x80',
        '\xdf', '\xef\xbf', '\xf7\xbf\xbf', '\xfb\xbf\xbf\xbf', '\xfd\xbf\xbf\xbf\xbf']
   for kk in k:
      vs.append((False, kk))

   # 3.4  Concatenation of incomplete sequences
   vs.append((False, ''.join(k)))

   # 3.5  Impossible bytes
   vs.append((False, '\xfe'))
   vs.append((False, '\xff'))
   vs.append((False, '\xfe\xfe\xff\xff'))

   # 4.1  Examples of an overlong ASCII character
   vs.append((False, '\xc0\xaf'))
   vs.append((False, '\xe0\x80\xaf'))
   vs.append((False, '\xf0\x80\x80\xaf'))
   vs.append((False, '\xf8\x80\x80\x80\xaf'))
   vs.append((False, '\xfc\x80\x80\x80\x80\xaf'))

   # 4.2  Maximum overlong sequences
   vs.append((False, '\xc1\xbf'))
   vs.append((False, '\xe0\x9f\xbf'))
   vs.append((False, '\xf0\x8f\xbf\xbf'))
   vs.append((False, '\xf8\x87\xbf\xbf\xbf'))
   vs.append((False, '\xfc\x83\xbf\xbf\xbf\xbf'))

   # 4.3  Overlong representation of the NUL character
   vs.append((False, '\xc0\x80'))
   vs.append((False, '\xe0\x80\x80'))
   vs.append((False, '\xf0\x80\x80\x80'))
   vs.append((False, '\xf8\x80\x80\x80\x80'))
   vs.append((False, '\xfc\x80\x80\x80\x80\x80'))

   # All Unicode code points
   for i in xrange(0, 0xffff): # should by 0x10ffff, but non-wide Python build is limited to 16-bits
      ss = unichr(i).encode("utf-8")
      if i >= 0xD800 and i <= 0xDBFF: # high-surrogate
         expect = None # False
      elif i >= 0xDC00 and i <= 0xDFFF: # low-surrogate
         expect = None # False
      else:
         expect = True
      if expect is not None:
         vs.append((expect, ss))

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

   # 5.3 Other illegal code positions
   vs.append((False, '\xef\xbf\xbe'))
   vs.append((False, '\xef\xbf\xbf'))


   for s in vs:
      v.reset()
      res = v.validate(bytearray(s[1]))
      try:
         ps = s[1].decode("utf-8")
         res_py = True
      except UnicodeDecodeError:
         res_py = False
      if res[0] != s[0]:
         print s, res
#      if res[0] != res_py:
#         print s, res_py
      #assert res[0] == s[0]

   sys.exit(0)

   # note that this source file was created with an UTF-8 editor and
   # declares that on line 1 to Python
   s = "µ@ßöäüàá"
   print s.decode("utf-8")
   print v.validate(bytearray(s))
   v.reset()
   print

   print v.validate(bytearray([0xF5]))
   v.reset()
   print

   ## the following 3 all fail on eating byte 7 (0xA0)
   print v.validate(bytearray([0x65, 0x64, 0x69, 0x74, 0x65, 0x64]))
   print v.validate(bytearray([0xED, 0xA0, 0x80]))
   v.reset()
   print

   print v.validate(bytearray([0x65, 0x64, 0x69, 0x74]))
   print v.validate(bytearray([0x65, 0x64, 0xED, 0xA0, 0x80]))
   v.reset()
   print

   print v.validate(bytearray([0x65, 0x64, 0x69, 0x74, 0x65, 0x64, 0xED]))
   print v.validate(bytearray([0xA0, 0x80]))
   v.reset()
   print
