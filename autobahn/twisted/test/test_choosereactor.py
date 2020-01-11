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

import sys
from unittest.mock import Mock

import twisted.internet
from twisted.trial import unittest

from autobahn.twisted import choosereactor


class ChooseReactorTests(unittest.TestCase):

    def patch_reactor(self, name, new_reactor):
        """
        Patch ``name`` so that Twisted will grab a fake reactor instead of
        a real one.
        """
        if hasattr(twisted.internet, name):
            self.patch(twisted.internet, name, new_reactor)
        else:
            def _cleanup():
                delattr(twisted.internet, name)
            setattr(twisted.internet, name, new_reactor)

    def patch_modules(self):
        """
        Patch ``sys.modules`` so that Twisted believes there is no
        installed reactor.
        """
        old_modules = dict(sys.modules)

        new_modules = dict(sys.modules)
        del new_modules["twisted.internet.reactor"]

        def _cleanup():
            sys.modules = old_modules

        self.addCleanup(_cleanup)
        sys.modules = new_modules

    def test_unknown(self):
        """
        ``install_optimal_reactor`` will use the default reactor if it is
        unable to detect the platform it is running on.
        """
        reactor_mock = Mock()
        self.patch_reactor("selectreactor", reactor_mock)
        self.patch(sys, "platform", "unknown")

        # Emulate that a reactor has not been installed
        self.patch_modules()

        choosereactor.install_optimal_reactor()
        reactor_mock.install.assert_called_once_with()

    def test_mac(self):
        """
        ``install_optimal_reactor`` will install KQueueReactor on
        Darwin (OS X).
        """
        reactor_mock = Mock()
        self.patch_reactor("kqreactor", reactor_mock)
        self.patch(sys, "platform", "darwin")

        # Emulate that a reactor has not been installed
        self.patch_modules()

        choosereactor.install_optimal_reactor()
        reactor_mock.install.assert_called_once_with()

    def test_win(self):
        """
        ``install_optimal_reactor`` will install IOCPReactor on Windows.
        """
        if sys.platform != 'win32':
            raise unittest.SkipTest('unit test requires Windows')

        reactor_mock = Mock()
        self.patch_reactor("iocpreactor", reactor_mock)
        self.patch(sys, "platform", "win32")

        # Emulate that a reactor has not been installed
        self.patch_modules()

        choosereactor.install_optimal_reactor()
        reactor_mock.install.assert_called_once_with()

    def test_bsd(self):
        """
        ``install_optimal_reactor`` will install KQueueReactor on BSD.
        """
        reactor_mock = Mock()
        self.patch_reactor("kqreactor", reactor_mock)
        self.patch(sys, "platform", "freebsd11")

        # Emulate that a reactor has not been installed
        self.patch_modules()

        choosereactor.install_optimal_reactor()
        reactor_mock.install.assert_called_once_with()

    def test_linux(self):
        """
        ``install_optimal_reactor`` will install EPollReactor on Linux.
        """
        reactor_mock = Mock()
        self.patch_reactor("epollreactor", reactor_mock)
        self.patch(sys, "platform", "linux")

        # Emulate that a reactor has not been installed
        self.patch_modules()

        choosereactor.install_optimal_reactor()
        reactor_mock.install.assert_called_once_with()
