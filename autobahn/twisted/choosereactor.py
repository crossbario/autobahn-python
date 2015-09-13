###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
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

from autobahn._logging import make_logger

__all__ = (
    'install_optimal_reactor',
    'install_reactor'
)


def install_optimal_reactor(verbose=False):
    """
    Try to install the optimal Twisted reactor for this platform.

    :param verbose: If ``True``, print what happens.
    :type verbose: bool
    """
    log = make_logger("twisted")

    import sys
    from twisted.python import reflect
    import txaio
    txaio.use_twisted()  # just to be sure...
    # XXX should I configure txaio.config.loop in here too, or just in
    # install_reactor()? (I am: see bottom of function)

    # determine currently installed reactor, if any
    ##
    if 'twisted.internet.reactor' in sys.modules:
        current_reactor = reflect.qual(sys.modules['twisted.internet.reactor'].__class__).split('.')[-1]
    else:
        current_reactor = None

    # depending on platform, install optimal reactor
    ##
    if 'bsd' in sys.platform or sys.platform.startswith('darwin'):

        # *BSD and MacOSX
        ##
        if current_reactor != 'KQueueReactor':
            try:
                from twisted.internet import kqreactor
                kqreactor.install()
            except Exception:
                log.failure(("Running on *BSD or MacOSX, but cannot install kqueue Twisted reactor\n"
                             "{log_failure.getTraceback()}"))
            else:
                log.debug("Running on *BSD or MacOSX and optimal reactor (kqueue) was installed.")
        else:
            log.debug("Running on *BSD or MacOSX and optimal reactor (kqueue) already installed.")

    elif sys.platform in ['win32']:

        # Windows
        ##
        if current_reactor != 'IOCPReactor':
            try:
                from twisted.internet.iocpreactor import reactor as iocpreactor
                iocpreactor.install()
            except Exception:
                log.failure(("Running on Windows, but cannot install IOCP Twisted reactor\n"
                             "{log_failure.getTraceback()"))
            else:
                log.debug("Running on Windows and optimal reactor (ICOP) was installed.")
        else:
            log.debug("Running on Windows and optimal reactor (ICOP) already installed.")

    elif sys.platform.startswith('linux'):

        # Linux
        ##
        if current_reactor != 'EPollReactor':
            try:
                from twisted.internet import epollreactor
                epollreactor.install()
            except Exception:
                log.failure(("Running on Linux, but cannot install Epoll Twisted reactor",
                             "{log_failure.getTraceback()"))
            else:
                log.debug("Running on Linux and optimal reactor (epoll) was installed.")
        else:
            log.debug("Running on Linux and optimal reactor (epoll) already installed.")

    else:
        try:
            from twisted.internet import default as defaultreactor
            defaultreactor.install()
        except Exception:
            log.failure(("Could not install default Twisted reactor for this platform"
                         "{log_failure.getTraceback()"))

    from twisted.internet import reactor
    txaio.config.loop = reactor


def install_reactor(explicit_reactor=None, verbose=False):
    """
    Install Twisted reactor.

    :param explicit_reactor: If provided, install this reactor. Else, install
        the optimal reactor.
    :type explicit_reactor: obj
    :param verbose: If ``True``, print what happens.
    :type verbose: bool
    """
    import sys
    import txaio
    txaio.use_twisted()  # just to be sure...

    log = make_logger("twisted")

    if explicit_reactor:
        # install explicitly given reactor
        ##
        from twisted.application.reactors import installReactor
        log.info("Trying to install explicitly specified Twisted reactor '{reactor}'", reactor=explicit_reactor)
        try:
            installReactor(explicit_reactor)
        except Exception:
            log.failure("Could not install Twisted reactor {reactor}\n{log_failure.getTraceback()}",
                        reactor=explicit_reactor)
            sys.exit(1)
    else:
        # automatically choose optimal reactor
        ##
        log.debug("Automatically choosing optimal Twisted reactor")
        install_optimal_reactor(verbose)

    # now the reactor is installed, import it
    from twisted.internet import reactor
    txaio.config.loop = reactor

    if verbose:
        from twisted.python.reflect import qual
        log.debug("Running Twisted reactor {reactor}", reactor=qual(reactor.__class__))

    return reactor
