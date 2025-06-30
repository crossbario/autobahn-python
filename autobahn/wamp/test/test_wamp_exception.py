###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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

from unittest import TestCase

from autobahn.wamp.exception import ApplicationError


class ApplicationErrorTestCase(TestCase):
    def test_unicode_str(self):
        """
        Unicode arguments in ApplicationError will not raise an exception when
        str()'d.
        """
        error = ApplicationError("some.url", "\u2603")
        self.assertIn("\u2603", str(error))

    def test_unicode_errormessage(self):
        """
        Unicode arguments in ApplicationError will not raise an exception when
        the error_message method is called.
        """
        error = ApplicationError("some.url", "\u2603")
        # on py27-tw189: exceptions.UnicodeEncodeError: 'ascii' codec can't encode character '\u2603' in position 10: ordinal not in
        print(error.error_message())
        self.assertIn("\u2603", error.error_message())
