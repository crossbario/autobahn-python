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

import six

__all__ = (
    'ComponentConfig',
    'HelloReturn',
    'Accept',
    'Deny',
    'Challenge',
    'HelloDetails',
    'SessionDetails',
    'CloseDetails',
    'SubscribeOptions',
    'EventDetails',
    'PublishOptions',
    'RegisterOptions',
    'CallDetails',
    'CallOptions',
    'CallResult',
)


class ComponentConfig(object):
    """
    WAMP application component configuration. An instance of this class is
    provided to the constructor of :class:`autobahn.wamp.protocol.ApplicationSession`.
    """

    def __init__(self, realm=None, extra=None):
        """
        :param realm: The realm the session should join.
        :type realm: unicode

        :param extra: Optional user-supplied object with extra
            configuration. This can be any object you like, and is
            accessible in your `ApplicationSession` subclass via
            `self.config.extra`. `dict` is a good default choice.
        """
        if six.PY2 and type(realm) == str:
            realm = six.u(realm)
        self.realm = realm
        self.extra = extra

    def __str__(self):
        return "ComponentConfig(realm = {0}, extra = {1})".format(self.realm, self.extra)


class HelloReturn(object):
    """
    Base class for ``HELLO`` return information.
    """


class Accept(HelloReturn):
    """
    Information to accept a ``HELLO``.
    """

    def __init__(self, authid=None, authrole=None, authmethod=None, authprovider=None):
        """

        :param authid: The authentication ID the client is assigned, e.g. ``"joe"`` or ``"joe@example.com"``.
        :type authid: unicode
        :param authrole: The authentication role the client is assigned, e.g. ``"anonymous"``, ``"user"`` or ``"com.myapp.user"``.
        :type authrole: unicode
        :param authmethod: The authentication method that was used to authenticate the client, e.g. ``"cookie"`` or ``"wampcra"``.
        :type authmethod: unicode
        :param authprovider: The authentication provider that was used to authenticate the client, e.g. ``"mozilla-persona"``.
        :type authprovider: unicode
        """
        if six.PY2:
            if type(authid) == str:
                authid = six.u(authid)
            if type(authrole) == str:
                authrole = six.u(authrole)
            if type(authmethod) == str:
                authmethod = six.u(authmethod)
            if type(authprovider) == str:
                authprovider = six.u(authprovider)

        assert(authid is None or type(authid) == six.text_type)
        assert(authrole is None or type(authrole) == six.text_type)
        assert(authmethod is None or type(authmethod) == six.text_type)
        assert(authprovider is None or type(authprovider) == six.text_type)

        self.authid = authid
        self.authrole = authrole
        self.authmethod = authmethod
        self.authprovider = authprovider

    def __str__(self):
        return "Accept(authid = {0}, authrole = {1}, authmethod = {2}, authprovider = {3})".format(self.authid, self.authrole, self.authmethod, self.authprovider)


class Deny(HelloReturn):
    """
    Information to deny a ``HELLO``.
    """

    def __init__(self, reason=u"wamp.error.not_authorized", message=None):
        """

        :param reason: The reason of denying the authentication (an URI, e.g. ``wamp.error.not_authorized``)
        :type reason: unicode
        :param message: A human readable message (for logging purposes).
        :type message: unicode
        """
        if six.PY2:
            if type(reason) == str:
                reason = six.u(reason)
            if type(message) == str:
                message = six.u(message)

        assert(type(reason) == six.text_type)
        assert(message is None or type(message) == six.text_type)

        self.reason = reason
        self.message = message

    def __str__(self):
        return "Deny(reason = {0}, message = '{1}')".format(self.reason, self.message)


class Challenge(HelloReturn):
    """
    Information to challenge the client upon ``HELLO``.
    """

    def __init__(self, method, extra=None):
        """

        :param method: The authentication method for the challenge (e.g. ``"wampcra"``).
        :type method: unicode
        :param extra: Any extra information for the authentication challenge. This is
           specific to the authentication method.
        :type extra: dict
        """
        if six.PY2:
            if type(method) == str:
                method = six.u(method)

        self.method = method
        self.extra = extra or {}

    def __str__(self):
        return "Challenge(method = {0}, extra = {1})".format(self.method, self.extra)


class HelloDetails(object):
    """
    Provides details of a WAMP session while still attaching.
    """

    def __init__(self, roles=None, authmethods=None, authid=None, pending_session=None):
        """

        :param roles: The WAMP roles and features supported by the attaching client.
        :type roles: dict
        :param authmethods: The authentication methods the client is willing to perform.
        :type authmethods: list
        :param authid: The authentication ID the client wants to authenticate as. Required for WAMP-CRA.
        :type authid: str
        :param pending_session: The session ID the session will get once successfully attached.
        :type pending_session: int
        """
        self.roles = roles
        self.authmethods = authmethods
        self.authid = authid
        self.pending_session = pending_session

    def __str__(self):
        return "HelloDetails(roles = {0}, authmethods = {1}, authid = {2}, pending_session = {3})".format(self.roles, self.authmethods, self.authid, self.pending_session)


class SessionDetails(object):
    """
    Provides details for a WAMP session upon open.

    .. seealso:: :func:`autobahn.wamp.interfaces.ISession.onJoin`
    """

    def __init__(self, realm, session, authid=None, authrole=None, authmethod=None, authprovider=None):
        """
        Ctor.

        :param realm: The realm this WAMP session is attached to.
        :type realm: unicode
        :param session: WAMP session ID of this session.
        :type session: int
        """
        self.realm = realm
        self.session = session
        self.authid = authid
        self.authrole = authrole
        self.authmethod = authmethod
        self.authprovider = authprovider

    def __str__(self):
        return "SessionDetails(realm = {0}, session = {1}, authid = {2}, authrole = {3}, authmethod = {4})".format(self.realm, self.session, self.authid, self.authrole, self.authmethod)


class CloseDetails(object):
    """
    Provides details for a WAMP session upon open.

    .. seealso:: :func:`autobahn.wamp.interfaces.ISession.onLeave`
    """
    REASON_DEFAULT = u"wamp.close.normal"
    REASON_TRANSPORT_LOST = u"wamp.close.transport_lost"

    def __init__(self, reason=None, message=None):
        """

        :param reason: The close reason (an URI, e.g. ``wamp.close.normal``)
        :type reason: unicode
        :param message: Closing log message.
        :type message: unicode
        """
        self.reason = reason
        self.message = message

    def __repr__(self):
        return "CloseDetails(reason = {0}, message = '{1}'')".format(self.reason, self.message)


class SubscribeOptions(object):
    """
    Used to provide options for subscribing in
    :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`.
    """

    def __init__(self, match=None, details_arg=None):
        """
        :param match: The topic matching method to be used for the subscription.
        :type match: unicode
        :param details_arg: When invoking the handler, provide event details
          in this keyword argument to the callable.
        :type details_arg: str
        """
        assert(match is None or (type(match) == six.text_type and match in [u'exact', u'prefix', u'wildcard']))
        assert(details_arg is None or type(details_arg) == str)

        self.match = match
        self.details_arg = details_arg

    def message_attr(self):
        # options dict as sent within WAMP message
        return {
            'match': self.match
        }

    def __str__(self):
        return "SubscribeOptions(match = {0}, details_arg = {1})".format(self.match, self.details_arg)


class EventDetails(object):
    """
    Provides details on an event when calling an event handler
    previously registered.
    """
    def __init__(self, publication, publisher=None, topic=None):
        """
        Ctor.

        :param publication: The publication ID of the event (always present).
        :type publication: int
        :param publisher: The WAMP session ID of the original publisher of this event.
        :type publisher: int
        :param topic: For pattern-based subscriptions, the actual topic URI being published to.
        :type topic1: unicode or None
        """
        self.publication = publication
        self.publisher = publisher
        self.topic = topic

    def __str__(self):
        return "EventDetails(publication = {0}, publisher = {1}, topic = {2})".format(self.publication, self.publisher, self.topic)


class PublishOptions(object):
    """
    Used to provide options for subscribing in
    :func:`autobahn.wamp.interfaces.IPublisher.publish`.
    """

    def __init__(self,
                 acknowledge=None,
                 exclude_me=None,
                 exclude=None,
                 eligible=None,
                 disclose_me=None):
        """

        :param acknowledge: If ``True``, acknowledge the publication with a success or
           error response.
        :type acknowledge: bool
        :param exclude_me: If ``True``, exclude the publisher from receiving the event, even
           if he is subscribed (and eligible).
        :type exclude_me: bool
        :param exclude: List of WAMP session IDs to exclude from receiving this event.
        :type exclude: list of int
        :param eligible: List of WAMP session IDs eligible to receive this event.
        :type eligible: list of int
        :param disclose_me: If ``True``, request to disclose the publisher of this event
           to subscribers.
        :type disclose_me: bool
        """
        # filter out None entries from exclude list, so it's easier for callers
        if type(exclude) == list:
            exclude = [x for x in exclude if x is not None]
        assert(acknowledge is None or type(acknowledge) == bool)
        assert(exclude_me is None or type(exclude_me) == bool)
        assert(exclude is None or (type(exclude) == list and all(type(x) in six.integer_types for x in exclude)))
        assert(eligible is None or (type(eligible) == list and all(type(x) in six.integer_types for x in eligible)))
        assert(disclose_me is None or type(disclose_me) == bool)

        self.acknowledge = acknowledge
        self.exclude_me = exclude_me
        self.exclude = exclude
        self.eligible = eligible
        self.disclose_me = disclose_me

    def message_attr(self):
        # options dict as sent within WAMP message
        return {
            u'acknowledge': self.acknowledge,
            u'exclude_me': self.exclude_me,
            u'exclude': self.exclude,
            u'eligible': self.eligible,
            u'disclose_me': self.disclose_me
        }

    def __str__(self):
        return "PublishOptions(acknowledge = {0}, exclude_me = {1}, exclude = {2}, eligible = {3}, disclose_me = {4})".format(self.acknowledge, self.exclude_me, self.exclude, self.eligible, self.disclose_me)


class RegisterOptions(object):
    """
    Used to provide options for registering in
    :func:`autobahn.wamp.interfaces.ICallee.register`.
    """

    def __init__(self, match=None, invoke=None, details_arg=None):
        """

        :param details_arg: When invoking the endpoint, provide call details
           in this keyword argument to the callable.
        :type details_arg: str
        """
        assert(match is None or (type(match) == six.text_type and match in [u'exact', u'prefix', u'wildcard']))
        assert(invoke is None or (type(invoke) == six.text_type and invoke in [u'single', u'first', u'last', u'roundrobin', u'random']))
        assert(details_arg is None or type(details_arg) == str)

        self.match = match
        self.invoke = invoke
        self.details_arg = details_arg

    def message_attr(self):
        # options dict as sent within WAMP message
        return {
            u'match': self.match,
            u'invoke': self.invoke
        }

    def __str__(self):
        return "RegisterOptions(match = {0}, invoke = {1}, details_arg = {2})".format(self.match, self.invoke, self.details_arg)


class CallDetails(object):
    """
    Provides details on a call when an endpoint previously
    registered is being called and opted to receive call details.
    """

    def __init__(self, progress=None, caller=None, procedure=None):
        """
        Ctor.

        :param progress: A callable that will receive progressive call results.
        :type progress: callable
        :param caller: The WAMP session ID of the caller, if the latter is disclosed.
        :type caller: int
        :param procedure: For pattern-based registrations, the actual procedure URI being called.
        :type procedure: unicode or None
        """
        self.progress = progress
        self.caller = caller
        self.procedure = procedure

    def __str__(self):
        return "CallDetails(progress = {0}, caller = {1}, procedure = {2})".format(self.progress, self.caller, self.procedure)


class CallOptions(object):
    """
    Used to provide options for calling with :func:`autobahn.wamp.interfaces.ICaller.call`.
    """

    def __init__(self,
                 on_progress=None,
                 timeout=None,
                 disclose_me=None):
        """

        :param on_progress: A callback that will be called when the remote endpoint
           called yields interim call progress results.
        :type on_progress: callable
        :param timeout: Time in seconds after which the call should be automatically canceled.
        :type timeout: float
        :param disclose_me: Request to disclose the identity of the caller (it's WAMP session ID)
           to Callees. Note that a Dealer, depending on Dealer configuration, might
           reject the request, or might disclose the Callee's identity without
           a request to do so.
        :type disclose_me: bool
        """
        assert(on_progress is None or callable(on_progress))
        assert(timeout is None or (type(timeout) in list(six.integer_types) + [float] and timeout > 0))
        assert(disclose_me is None or type(disclose_me) == bool)

        self.on_progress = on_progress
        self.timeout = timeout
        self.disclose_me = disclose_me

    def message_attr(self):
        # options dict as sent within WAMP message
        res = {
            u'timeout': self.timeout,
            u'disclose_me': self.disclose_me
        }
        if self.on_progress:
            res['receive_progress'] = True
        return res

    def __str__(self):
        return "CallOptions(on_progress = {0}, timeout = {1}, disclose_me = {2})".format(self.on_progress, self.timeout, self.disclose_me)


class CallResult(object):
    """
    Wrapper for remote procedure call results that contain multiple positional
    return values or keyword return values.
    """

    def __init__(self, *results, **kwresults):
        """
        Constructor.

        :param results: The positional result values.
        :type results: list
        :param kwresults: The keyword result values.
        :type kwresults: dict
        """
        self.results = results
        self.kwresults = kwresults

    def __str__(self):
        return "CallResult(results = {0}, kwresults = {1})".format(self.results, self.kwresults)
