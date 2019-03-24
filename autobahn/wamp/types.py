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

from autobahn.util import public

from autobahn.wamp.request import Subscription, Registration


__all__ = (
    'ComponentConfig',
    'HelloReturn',
    'Accept',
    'Deny',
    'Challenge',
    'HelloDetails',
    'SessionDetails',
    'SessionIdent',
    'CloseDetails',
    'SubscribeOptions',
    'EventDetails',
    'PublishOptions',
    'RegisterOptions',
    'CallDetails',
    'CallOptions',
    'CallResult',
    'EncodedPayload'
)


@public
class ComponentConfig(object):
    """
    WAMP application component configuration. An instance of this class is
    provided to the constructor of :class:`autobahn.wamp.protocol.ApplicationSession`.
    """

    __slots__ = (
        'realm',
        'extra',
        'keyring',
        'controller',
        'shared',
        'runner',
    )

    def __init__(self, realm=None, extra=None, keyring=None, controller=None, shared=None, runner=None):
        """

        :param realm: The realm the session would like to join or ``None`` to let the router
            auto-decide the realm (if the router is configured and allowing to do so).
        :type realm: str

        :param extra: Optional user-supplied object with extra configuration.
            This can be any object you like, and is accessible in your
            `ApplicationSession` subclass via `self.config.extra`. `dict` is
            a good default choice. Important: if the component is to be hosted
            by Crossbar.io, the supplied value must be JSON serializable.
        :type extra: arbitrary

        :param keyring: A mapper from WAMP URIs to "from"/"to" Ed25519 keys. When using
            WAMP end-to-end encryption, application payload is encrypted using a
            symmetric message key, which in turn is encrypted using the "to" URI (topic being
            published to or procedure being called) public key and the "from" URI
            private key. In both cases, the key for the longest matching URI is used.
        :type keyring: obj implementing IKeyRing or None

        :param controller: A WAMP ApplicationSession instance that holds a session to
            a controlling entity. This optional feature needs to be supported by a WAMP
            component hosting run-time.
        :type controller: instance of ApplicationSession or None

        :param shared: A dict object to exchange user information or hold user objects shared
            between components run under the same controlling entity. This optional feature
            needs to be supported by a WAMP component hosting run-time. Use with caution, as using
            this feature can introduce coupling between components. A valid use case would be
            to hold a shared database connection pool.
        :type shared: dict or None

        :param runner: Instance of ApplicationRunner when run under this.
        :type runner: :class:`autobahn.twisted.wamp.ApplicationRunner`
        """
        assert(realm is None or type(realm) == six.text_type)
        # assert(keyring is None or ...) # FIXME

        self.realm = realm
        self.extra = extra
        self.keyring = keyring
        self.controller = controller
        self.shared = shared
        self.runner = runner

    def __str__(self):
        return u"ComponentConfig(realm=<{}>, extra={}, keyring={}, controller={}, shared={}, runner={})".format(self.realm, self.extra, self.keyring, self.controller, self.shared, self.runner)


@public
class HelloReturn(object):
    """
    Base class for ``HELLO`` return information.
    """


@public
class Accept(HelloReturn):
    """
    Information to accept a ``HELLO``.
    """

    __slots__ = (
        'realm',
        'authid',
        'authrole',
        'authmethod',
        'authprovider',
        'authextra',
    )

    def __init__(self, realm=None, authid=None, authrole=None, authmethod=None, authprovider=None, authextra=None):
        """

        :param realm: The realm the client is joined to.
        :type realm: str

        :param authid: The authentication ID the client is assigned, e.g. ``"joe"`` or ``"joe@example.com"``.
        :type authid: str

        :param authrole: The authentication role the client is assigned, e.g. ``"anonymous"``, ``"user"`` or ``"com.myapp.user"``.
        :type authrole: str

        :param authmethod: The authentication method that was used to authenticate the client, e.g. ``"cookie"`` or ``"wampcra"``.
        :type authmethod: str

        :param authprovider: The authentication provider that was used to authenticate the client, e.g. ``"mozilla-persona"``.
        :type authprovider: str

        :param authextra: Application-specific authextra to be forwarded to the client in `WELCOME.details.authextra`.
        :type authextra: dict
        """
        assert(realm is None or type(realm) == six.text_type)
        assert(authid is None or type(authid) == six.text_type)
        assert(authrole is None or type(authrole) == six.text_type)
        assert(authmethod is None or type(authmethod) == six.text_type)
        assert(authprovider is None or type(authprovider) == six.text_type)
        assert(authextra is None or type(authextra) == dict)

        self.realm = realm
        self.authid = authid
        self.authrole = authrole
        self.authmethod = authmethod
        self.authprovider = authprovider
        self.authextra = authextra

    def __str__(self):
        return u"Accept(realm=<{}>, authid=<{}>, authrole=<{}>, authmethod={}, authprovider={}, authextra={})".format(self.realm, self.authid, self.authrole, self.authmethod, self.authprovider, self.authextra)


@public
class Deny(HelloReturn):
    """
    Information to deny a ``HELLO``.
    """

    __slots__ = (
        'reason',
        'message',
    )

    def __init__(self, reason=u'wamp.error.not_authorized', message=None):
        """

        :param reason: The reason of denying the authentication (an URI, e.g. ``u'wamp.error.not_authorized'``)
        :type reason: str

        :param message: A human readable message (for logging purposes).
        :type message: str
        """
        assert(type(reason) == six.text_type)
        assert(message is None or type(message) == six.text_type)

        self.reason = reason
        self.message = message

    def __str__(self):
        return u"Deny(reason=<{}>, message='{}')".format(self.reason, self.message)


@public
class Challenge(HelloReturn):
    """
    Information to challenge the client upon ``HELLO``.
    """

    __slots__ = (
        'method',
        'extra',
    )

    def __init__(self, method, extra=None):
        """

        :param method: The authentication method for the challenge (e.g. ``"wampcra"``).
        :type method: str

        :param extra: Any extra information for the authentication challenge. This is
           specific to the authentication method.
        :type extra: dict
        """
        assert(type(method) == six.text_type)
        assert(extra is None or type(extra) == dict)

        self.method = method
        self.extra = extra or {}

    def __str__(self):
        return u"Challenge(method={}, extra={})".format(self.method, self.extra)


@public
class HelloDetails(object):
    """
    Provides details of a WAMP session while still attaching.
    """

    __slots__ = (
        'realm',
        'authmethods',
        'authid',
        'authrole',
        'authextra',
        'session_roles',
        'pending_session',
        'resumable',
        'resume_session',
        'resume_token',
    )

    def __init__(self, realm=None, authmethods=None, authid=None, authrole=None, authextra=None, session_roles=None, pending_session=None, resumable=None, resume_session=None, resume_token=None):
        """

        :param realm: The realm the client wants to join.
        :type realm: str or None

        :param authmethods: The authentication methods the client is willing to perform.
        :type authmethods: list of str or None

        :param authid: The authid the client wants to authenticate as.
        :type authid: str or None

        :param authrole: The authrole the client wants to authenticate as.
        :type authrole: str or None

        :param authextra: Any extra information the specific authentication method requires the client to send.
        :type authextra: arbitrary or None

        :param session_roles: The WAMP session roles and features by the connecting client.
        :type session_roles: dict or None

        :param pending_session: The session ID the session will get once successfully attached.
        :type pending_session: int or None

        :param resumable:
        :type resumable: bool or None

        :param resume_session: The session the client would like to resume.
        :type resume_session: int or None

        :param resume_token: The secure authorisation token to resume the session.
        :type resume_token: str or None
        """
        assert(realm is None or type(realm) == six.text_type)
        assert(authmethods is None or (type(authmethods) == list and all(type(x) == six.text_type for x in authmethods)))
        assert(authid is None or type(authid) == six.text_type)
        assert(authrole is None or type(authrole) == six.text_type)
        assert(authextra is None or type(authextra) == dict)
        # assert(session_roles is None or ...)  # FIXME
        assert(pending_session is None or type(pending_session) in six.integer_types)
        assert(resumable is None or type(resumable) == bool)
        assert(resume_session is None or type(resume_session) == int)
        assert(resume_token is None or type(resume_token) == six.text_type)

        self.realm = realm
        self.authmethods = authmethods
        self.authid = authid
        self.authrole = authrole
        self.authextra = authextra
        self.session_roles = session_roles
        self.pending_session = pending_session
        self.resumable = resumable
        self.resume_session = resume_session
        self.resume_token = resume_token

    def __str__(self):
        return u"HelloDetails(realm=<{}>, authmethods={}, authid=<{}>, authrole=<{}>, authextra={}, session_roles={}, pending_session={}, resumable={}, resume_session={}, resume_token={})".format(self.realm, self.authmethods, self.authid, self.authrole, self.authextra, self.session_roles, self.pending_session, self.resumable, self.resume_session, self.resume_token)


@public
class SessionDetails(object):
    """
    Provides details for a WAMP session upon open.

    .. seealso:: :func:`autobahn.wamp.interfaces.ISession.onJoin`
    """

    __slots__ = (
        'realm',
        'session',
        'authid',
        'authrole',
        'authmethod',
        'authprovider',
        'authextra',
        'resumed',
        'resumable',
        'resume_token',
    )

    def __init__(self, realm, session, authid=None, authrole=None, authmethod=None, authprovider=None, authextra=None, resumed=None, resumable=None, resume_token=None):
        """

        :param realm: The realm this WAMP session is attached to.
        :type realm: str

        :param session: WAMP session ID of this session.
        :type session: int

        :param resumed: Whether the session is a resumed one.
        :type resumed: bool or None

        :param resumable: Whether this session can be resumed later.
        :type resumable: bool or None

        :param resume_token: The secure authorisation token to resume the session.
        :type resume_token: str or None
        """
        assert(type(realm) == six.text_type)
        assert(type(session) in six.integer_types)
        assert(authid is None or type(authid) == six.text_type)
        assert(authrole is None or type(authrole) == six.text_type)
        assert(authmethod is None or type(authmethod) == six.text_type)
        assert(authprovider is None or type(authprovider) == six.text_type)
        assert(authextra is None or type(authextra) == dict)
        assert(resumed is None or type(resumed) == bool)
        assert(resumable is None or type(resumable) == bool)
        assert(resume_token is None or type(resume_token) == six.text_type)

        self.realm = realm
        self.session = session
        self.authid = authid
        self.authrole = authrole
        self.authmethod = authmethod
        self.authprovider = authprovider
        self.authextra = authextra
        self.resumed = resumed
        self.resumable = resumable
        self.resume_token = resume_token

    def marshal(self):
        obj = {
            u'realm': self.realm,
            u'session': self.session,
            u'authid': self.authid,
            u'authrole': self.authrole,
            u'authmethod': self.authmethod,
            u'authprovider': self.authprovider,
            u'authextra': self.authextra,
            u'resumed': self.resumed,
            u'resumable': self.resumable,
            u'resume_token': self.resume_token
        }
        return obj

    def __str__(self):
        return u"SessionDetails(realm=<{}>, session={}, authid=<{}>, authrole=<{}>, authmethod={}, authprovider={}, authextra={}, resumed={}, resumable={}, resume_token={})".format(self.realm, self.session, self.authid, self.authrole, self.authmethod, self.authprovider, self.authextra, self.resumed, self.resumable, self.resume_token)


@public
class SessionIdent(object):
    """
    WAMP session identification information.

    A WAMP session joined on a realm on a WAMP router is identified technically
    by its session ID (``session``) already.

    The permissions the session has are tied to the WAMP authentication role (``authrole``).

    The subject behind the session, eg the user or the application component is identified
    by the WAMP authentication ID (``authid``). One session is always authenticated under/as
    one specific ``authid``, but a given ``authid`` might have zero, one or many sessions
    joined on a router at the same time.
    """

    __slots__ = (
        'session',
        'authid',
        'authrole',
    )

    def __init__(self, session=None, authid=None, authrole=None):
        """

        :param session: WAMP session ID of the session.
        :type session: int

        :param authid: The WAMP authid of the session.
        :type authid: str

        :param authrole: The WAMP authrole of the session.
        :type authrole: str
        """
        assert(session is None or type(session) in six.integer_types)
        assert(authid is None or type(authid) == six.text_type)
        assert(type(authrole) == six.text_type)

        self.session = session
        self.authid = authid
        self.authrole = authrole

    def __str__(self):
        return u"SessionIdent(session={}, authid={}, authrole={})".format(self.session, self.authid, self.authrole)

    def marshal(self):
        obj = {
            u'session': self.session,
            u'authid': self.authid,
            u'authrole': self.authrole,
        }
        return obj

    @staticmethod
    def from_calldetails(call_details):
        """
        Create a new session identification object from the caller information
        in the call details provided.

        :param call_details: Details of a WAMP call.
        :type call_details: :class:`autobahn.wamp.types.CallDetails`

        :returns: New session identification object.
        :rtype: :class:`autobahn.wamp.types.SessionIdent`
        """
        assert isinstance(call_details, CallDetails)

        if call_details.forward_for:
            caller = call_details.forward_for[0]
            session_ident = SessionIdent(caller['session'],
                                         caller['authid'],
                                         caller['authrole'])
        else:
            session_ident = SessionIdent(call_details.caller,
                                         call_details.caller_authid,
                                         call_details.caller_authrole)
        return session_ident

    @staticmethod
    def from_eventdetails(event_details):
        """
        Create a new session identification object from the publisher information
        in the event details provided.

        :param event_details: Details of a WAMP event.
        :type event_details: :class:`autobahn.wamp.types.EventDetails`

        :returns: New session identification object.
        :rtype: :class:`autobahn.wamp.types.SessionIdent`
        """
        assert isinstance(event_details, EventDetails)

        if event_details.forward_for:
            publisher = event_details.forward_for[0]
            session_ident = SessionIdent(publisher['session'],
                                         publisher['authid'],
                                         publisher['authrole'])
        else:
            session_ident = SessionIdent(event_details.publisher,
                                         event_details.publisher_authid,
                                         event_details.publisher_authrole)
        return session_ident


@public
class CloseDetails(object):
    """
    Provides details for a WAMP session upon close.

    .. seealso:: :func:`autobahn.wamp.interfaces.ISession.onLeave`
    """
    REASON_DEFAULT = u"wamp.close.normal"
    REASON_TRANSPORT_LOST = u"wamp.close.transport_lost"

    __slots__ = (
        'reason',
        'message',
    )

    def __init__(self, reason=None, message=None):
        """

        :param reason: The close reason (an URI, e.g. ``wamp.close.normal``)
        :type reason: str

        :param message: Closing log message.
        :type message: str
        """
        assert(reason is None or type(reason) == six.text_type)
        assert(message is None or type(message) == six.text_type)

        self.reason = reason
        self.message = message

    def marshal(self):
        obj = {
            u'reason': self.reason,
            u'message': self.message
        }
        return obj

    def __str__(self):
        return u"CloseDetails(reason=<{}>, message='{}')".format(self.reason, self.message)


@public
class SubscribeOptions(object):
    """
    Used to provide options for subscribing in
    :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`.
    """

    __slots__ = (
        'match',
        'details',
        'details_arg',
        'get_retained',
        'forward_for',
        'correlation_id',
        'correlation_uri',
        'correlation_is_anchor',
        'correlation_is_last',
    )

    def __init__(self, match=None, details=None, details_arg=None, forward_for=None, get_retained=None,
                 correlation_id=None, correlation_uri=None, correlation_is_anchor=None,
                 correlation_is_last=None):
        """

        :param match: The topic matching method to be used for the subscription.
        :type match: str

        :param details: When invoking the handler, provide event details in a keyword
            parameter ``details``.
        :type details: bool

        :param details_arg: DEPCREATED (use "details" flag). When invoking the handler
            provide event details in this keyword argument to the callable.
        :type details_arg: str

        :param get_retained: Whether the client wants the retained message we may have along with the subscription.
        :type get_retained: bool or None
        """
        assert(match is None or (type(match) == six.text_type and match in [u'exact', u'prefix', u'wildcard']))
        assert(details is None or (type(details) == bool and details_arg is None))
        assert(details_arg is None or type(details_arg) == str)  # yes, "str" is correct here, since this is about Python identifiers!
        assert(get_retained is None or type(get_retained) is bool)

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        self.match = match

        # FIXME: this is for backwards compat, but we'll deprecate it in the future
        self.details = details
        if details:
            self.details_arg = 'details'
        else:
            self.details_arg = details_arg

        self.get_retained = get_retained
        self.forward_for = forward_for

        self.correlation_id = correlation_id
        self.correlation_uri = correlation_uri
        self.correlation_is_anchor = correlation_is_anchor
        self.correlation_is_last = correlation_is_last

    def message_attr(self):
        """
        Returns options dict as sent within WAMP messages.
        """
        options = {}

        if self.match is not None:
            options[u'match'] = self.match

        if self.get_retained is not None:
            options[u'get_retained'] = self.get_retained

        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        return options

    def __str__(self):
        return u"SubscribeOptions(match={}, details={}, details_arg={}, get_retained={}, forward_for={})".format(self.match, self.details, self.details_arg, self.get_retained, self.forward_for)


@public
class EventDetails(object):
    """
    Provides details on an event when calling an event handler
    previously registered.
    """

    __slots__ = (
        'subscription',
        'publication',
        'publisher',
        'publisher_authid',
        'publisher_authrole',
        'topic',
        'retained',
        'enc_algo',
        'forward_for',
    )

    def __init__(self, subscription, publication, publisher=None, publisher_authid=None, publisher_authrole=None,
                 topic=None, retained=None, enc_algo=None, forward_for=None):
        """

        :param subscription: The (client side) subscription object on which this event is delivered.
        :type subscription: instance of :class:`autobahn.wamp.request.Subscription`

        :param publication: The publication ID of the event (always present).
        :type publication: int

        :param publisher: The WAMP session ID of the original publisher of this event.
            Only filled when publisher is disclosed.
        :type publisher: None or int

        :param publisher_authid: The WAMP authid of the original publisher of this event.
            Only filled when publisher is disclosed.
        :type publisher_authid: str or None

        :param publisher_authrole: The WAMP authrole of the original publisher of this event.
            Only filled when publisher is disclosed.
        :type publisher_authrole: str or None

        :param topic: For pattern-based subscriptions, the actual topic URI being published to.
            Only filled for pattern-based subscriptions.
        :type topic: str or None

        :param retained: Whether the message was retained by the broker on the topic, rather than just published.
        :type retained: bool or None

        :param enc_algo: Payload encryption algorithm that
            was in use (currently, either ``None`` or ``u'cryptobox'``).
        :type enc_algo: str or None

        :param forward_for: When this Event is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert(isinstance(subscription, Subscription))
        assert(type(publication) in six.integer_types)
        assert(publisher is None or type(publisher) in six.integer_types)
        assert(publisher_authid is None or type(publisher_authid) == six.text_type)
        assert(publisher_authrole is None or type(publisher_authrole) == six.text_type)
        assert(topic is None or type(topic) == six.text_type)
        assert(retained is None or type(retained) is bool)
        assert(enc_algo is None or type(enc_algo) == six.text_type)
        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        self.subscription = subscription
        self.publication = publication
        self.publisher = publisher
        self.publisher_authid = publisher_authid
        self.publisher_authrole = publisher_authrole
        self.topic = topic
        self.retained = retained
        self.enc_algo = enc_algo
        self.forward_for = forward_for

    def __str__(self):
        return u"EventDetails(subscription={}, publication={}, publisher={}, publisher_authid={}, publisher_authrole={}, topic=<{}>, retained={}, enc_algo={}, forward_for={})".format(self.subscription, self.publication, self.publisher, self.publisher_authid, self.publisher_authrole, self.topic, self.retained, self.enc_algo, self.forward_for)


@public
class PublishOptions(object):
    """
    Used to provide options for subscribing in
    :func:`autobahn.wamp.interfaces.IPublisher.publish`.
    """

    __slots__ = (
        'acknowledge',
        'exclude_me',
        'exclude',
        'exclude_authid',
        'exclude_authrole',
        'eligible',
        'eligible_authid',
        'eligible_authrole',
        'retain',
        'forward_for',
        'correlation_id',
        'correlation_uri',
        'correlation_is_anchor',
        'correlation_is_last',
    )

    def __init__(self,
                 acknowledge=None,
                 exclude_me=None,
                 exclude=None,
                 exclude_authid=None,
                 exclude_authrole=None,
                 eligible=None,
                 eligible_authid=None,
                 eligible_authrole=None,
                 retain=None,
                 forward_for=None,
                 correlation_id=None,
                 correlation_uri=None,
                 correlation_is_anchor=None,
                 correlation_is_last=None):
        """

        :param acknowledge: If ``True``, acknowledge the publication with a success or
           error response.
        :type acknowledge: bool

        :param exclude_me: If ``True``, exclude the publisher from receiving the event, even
           if he is subscribed (and eligible).
        :type exclude_me: bool or None

        :param exclude: A single WAMP session ID or a list thereof to exclude from receiving this event.
        :type exclude: int or list of int or None

        :param exclude_authid: A single WAMP authid or a list thereof to exclude from receiving this event.
        :type exclude_authid: str or list of str or None

        :param exclude_authrole: A single WAMP authrole or a list thereof to exclude from receiving this event.
        :type exclude_authrole: list of str or None

        :param eligible: A single WAMP session ID or a list thereof eligible to receive this event.
        :type eligible: int or list of int or None

        :param eligible_authid: A single WAMP authid or a list thereof eligible to receive this event.
        :type eligible_authid: str or list of str or None

        :param eligible_authrole: A single WAMP authrole or a list thereof eligible to receive this event.
        :type eligible_authrole: str or list of str or None

        :param retain: If ``True``, request the broker retain this event.
        :type retain: bool or None

        :param forward_for: When this Event is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert(acknowledge is None or type(acknowledge) == bool)
        assert(exclude_me is None or type(exclude_me) == bool)
        assert(exclude is None or type(exclude) in six.integer_types or (type(exclude) == list and all(type(x) in six.integer_types for x in exclude)))
        assert(exclude_authid is None or type(exclude_authid) == six.text_type or (type(exclude_authid) == list and all(type(x) == six.text_type for x in exclude_authid)))
        assert(exclude_authrole is None or type(exclude_authrole) == six.text_type or (type(exclude_authrole) == list and all(type(x) == six.text_type for x in exclude_authrole)))
        assert(eligible is None or type(eligible) in six.integer_types or (type(eligible) == list and all(type(x) in six.integer_types for x in eligible)))
        assert(eligible_authid is None or type(eligible_authid) == six.text_type or (type(eligible_authid) == list and all(type(x) == six.text_type for x in eligible_authid)))
        assert(eligible_authrole is None or type(eligible_authrole) == six.text_type or (type(eligible_authrole) == list and all(type(x) == six.text_type for x in eligible_authrole)))
        assert(retain is None or type(retain) == bool)

        assert(forward_for is None or type(forward_for) == list), 'forward_for, when present, must have list type - was {}'.format(type(forward_for))
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict, 'forward_for must be type dict - was {}'.format(type(ff))
                assert 'session' in ff, 'forward_for must have session attribute'
                assert type(ff['session']) in six.integer_types, 'forward_for.session must have integer type - was {}'.format(type(ff['session']))
                assert 'authid' in ff, 'forward_for must have authid attributed'
                assert type(ff['authid']) == six.text_type, 'forward_for.authid must have str type - was {}'.format(type(ff['authid']))
                assert 'authrole' in ff, 'forward_for must have authrole attribute'
                assert type(ff['authrole']) == six.text_type, 'forward_for.authrole must have str type - was {}'.format(type(ff['authrole']))

        self.acknowledge = acknowledge
        self.exclude_me = exclude_me
        self.exclude = exclude
        self.exclude_authid = exclude_authid
        self.exclude_authrole = exclude_authrole
        self.eligible = eligible
        self.eligible_authid = eligible_authid
        self.eligible_authrole = eligible_authrole
        self.retain = retain
        self.forward_for = forward_for

        self.correlation_id = correlation_id
        self.correlation_uri = correlation_uri
        self.correlation_is_anchor = correlation_is_anchor
        self.correlation_is_last = correlation_is_last

    def message_attr(self):
        """
        Returns options dict as sent within WAMP messages.
        """
        options = {}

        if self.acknowledge is not None:
            options[u'acknowledge'] = self.acknowledge

        if self.exclude_me is not None:
            options[u'exclude_me'] = self.exclude_me

        if self.exclude is not None:
            options[u'exclude'] = self.exclude if type(self.exclude) == list else [self.exclude]

        if self.exclude_authid is not None:
            options[u'exclude_authid'] = self.exclude_authid if type(self.exclude_authid) == list else [self.exclude_authid]

        if self.exclude_authrole is not None:
            options[u'exclude_authrole'] = self.exclude_authrole if type(self.exclude_authrole) == list else [self.exclude_authrole]

        if self.eligible is not None:
            options[u'eligible'] = self.eligible if type(self.eligible) == list else [self.eligible]

        if self.eligible_authid is not None:
            options[u'eligible_authid'] = self.eligible_authid if type(self.eligible_authid) == list else [self.eligible_authid]

        if self.eligible_authrole is not None:
            options[u'eligible_authrole'] = self.eligible_authrole if type(self.eligible_authrole) == list else [self.eligible_authrole]

        if self.retain is not None:
            options[u'retain'] = self.retain

        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        return options

    def __str__(self):
        return u"PublishOptions(acknowledge={}, exclude_me={}, exclude={}, exclude_authid={}, exclude_authrole={}, eligible={}, eligible_authid={}, eligible_authrole={}, retain={}, forward_for={})".format(self.acknowledge, self.exclude_me, self.exclude, self.exclude_authid, self.exclude_authrole, self.eligible, self.eligible_authid, self.eligible_authrole, self.retain, self.forward_for)


@public
class RegisterOptions(object):
    """
    Used to provide options for registering in
    :func:`autobahn.wamp.interfaces.ICallee.register`.
    """

    __slots__ = (
        'match',
        'invoke',
        'concurrency',
        'force_reregister',
        'forward_for',
        'details',
        'details_arg',
        'correlation_id',
        'correlation_uri',
        'correlation_is_anchor',
        'correlation_is_last',
    )

    def __init__(self, match=None, invoke=None, concurrency=None, force_reregister=None, forward_for=None,
                 details=None, details_arg=None, correlation_id=None, correlation_uri=None,
                 correlation_is_anchor=None, correlation_is_last=None):
        """
        :param match: Type of matching to use on the URI (`exact`, `prefix` or `wildcard`)

        :param invoke: Type of invoke mechanism to use (`single`, `first`, `last`, `roundrobin`, `random`)

        :param concurrency: if used, the number of times a particular
            endpoint may be called concurrently (e.g. if this is 3, and
            there are already 3 calls in-progress a 4th call will receive
            an error)

        :param details_arg: When invoking the endpoint, provide call details
            in this keyword argument to the callable.
        :type details_arg: str

        :param details: When invoking the endpoint, provide call details in a keyword
            parameter ``details``.
        :type details: bool

        :param details_arg: DEPCREATED (use "details" flag). When invoking the endpoint,
            provide call details in this keyword argument to the callable.
        :type details_arg: str

        :param force_reregister: if True, any other session that has
            already registered this URI will be 'kicked out' and this
            session will become the one that's registered (the previous
            session must have used `force_reregister=True` as well)
        :type force_reregister: bool

        :param forward_for: When this Register is forwarded over a router-to-router link,
            or via an intermediary router.
        :type forward_for: list[dict]
        """
        assert(match is None or (type(match) == six.text_type and match in [u'exact', u'prefix', u'wildcard']))
        assert(invoke is None or (type(invoke) == six.text_type and invoke in [u'single', u'first', u'last', u'roundrobin', u'random']))
        assert(concurrency is None or (type(concurrency) in six.integer_types and concurrency > 0))
        assert(details is None or (type(details) == bool and details_arg is None))
        assert(details_arg is None or type(details_arg) == str)  # yes, "str" is correct here, since this is about Python identifiers!
        assert force_reregister in [None, True, False]

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        self.match = match
        self.invoke = invoke
        self.concurrency = concurrency
        self.force_reregister = force_reregister
        self.forward_for = forward_for

        # FIXME: this is for backwards compat, but we'll deprecate it in the future
        self.details = details
        if details:
            self.details_arg = 'details'
        else:
            self.details_arg = details_arg

        self.correlation_id = correlation_id
        self.correlation_uri = correlation_uri
        self.correlation_is_anchor = correlation_is_anchor
        self.correlation_is_last = correlation_is_last

    def message_attr(self):
        """
        Returns options dict as sent within WAMP messages.
        """
        options = {}

        if self.match is not None:
            options[u'match'] = self.match

        if self.invoke is not None:
            options[u'invoke'] = self.invoke

        if self.concurrency is not None:
            options[u'concurrency'] = self.concurrency

        if self.force_reregister is not None:
            options[u'force_reregister'] = self.force_reregister

        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        return options

    def __str__(self):
        return u"RegisterOptions(match={}, invoke={}, concurrency={}, details={}, details_arg={}, force_reregister={}, forward_for={})".format(self.match, self.invoke, self.concurrency, self.details, self.details_arg, self.force_reregister, self.forward_for)


@public
class CallDetails(object):
    """
    Provides details on a call when an endpoint previously
    registered is being called and opted to receive call details.
    """

    __slots__ = (
        'registration',
        'progress',
        'caller',
        'caller_authid',
        'caller_authrole',
        'procedure',
        'enc_algo',
        'forward_for',
    )

    def __init__(self, registration, progress=None, caller=None, caller_authid=None,
                 caller_authrole=None, procedure=None, enc_algo=None, forward_for=None):
        """

        :param registration: The (client side) registration object this invocation is delivered on.
        :type registration: instance of :class:`autobahn.wamp.request.Registration`

        :param progress: A callable that will receive progressive call results.
        :type progress: callable or None

        :param caller: The WAMP session ID of the caller, if the latter is disclosed.
            Only filled when caller is disclosed.
        :type caller: int or None

        :param caller_authid: The WAMP authid of the original caller of this event.
            Only filled when caller is disclosed.
        :type caller_authid: str or None

        :param caller_authrole: The WAMP authrole of the original caller of this event.
            Only filled when caller is disclosed.
        :type caller_authrole: str or None

        :param procedure: For pattern-based registrations, the actual procedure URI being called.
        :type procedure: str or None

        :param enc_algo: Payload encryption algorithm that
            was in use (currently, either `None` or `"cryptobox"`).
        :type enc_algo: str or None

        :param forward_for: When this Call is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert(isinstance(registration, Registration))
        assert(progress is None or callable(progress))
        assert(caller is None or type(caller) in six.integer_types)
        assert(caller_authid is None or type(caller_authid) == six.text_type)
        assert(caller_authrole is None or type(caller_authrole) == six.text_type)
        assert(procedure is None or type(procedure) == six.text_type)
        assert(enc_algo is None or type(enc_algo) == six.text_type)

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        self.registration = registration
        self.progress = progress
        self.caller = caller
        self.caller_authid = caller_authid
        self.caller_authrole = caller_authrole
        self.procedure = procedure
        self.enc_algo = enc_algo
        self.forward_for = forward_for

    def __str__(self):
        return u"CallDetails(registration={}, progress={}, caller={}, caller_authid={}, caller_authrole={}, procedure=<{}>, enc_algo={}, forward_for={})".format(self.registration, self.progress, self.caller, self.caller_authid, self.caller_authrole, self.procedure, self.enc_algo, self.forward_for)


@public
class CallOptions(object):
    """
    Used to provide options for calling with :func:`autobahn.wamp.interfaces.ICaller.call`.
    """

    __slots__ = (
        'on_progress',
        'timeout',
        'caller',
        'caller_authid',
        'caller_authrole',
        'forward_for',
        'correlation_id',
        'correlation_uri',
        'correlation_is_anchor',
        'correlation_is_last',
        'details',
    )

    def __init__(self,
                 on_progress=None,
                 timeout=None,
                 caller=None,
                 caller_authid=None,
                 caller_authrole=None,
                 forward_for=None,
                 correlation_id=None,
                 correlation_uri=None,
                 correlation_is_anchor=None,
                 correlation_is_last=None,
                 details=None):
        """

        :param on_progress: A callback that will be called when the remote endpoint
           called yields interim call progress results.
        :type on_progress: callable

        :param timeout: Time in seconds after which the call should be automatically canceled.
        :type timeout: float

        :param forward_for: When this Call is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert(on_progress is None or callable(on_progress))
        assert(timeout is None or (type(timeout) in list(six.integer_types) + [float] and timeout > 0))
        assert(details is None or type(details) == bool)
        assert(caller is None or type(caller) in six.integer_types)
        assert(caller_authid is None or type(caller_authid) == six.text_type)
        assert(caller_authrole is None or type(caller_authrole) == six.text_type)
        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        self.on_progress = on_progress
        self.timeout = timeout

        self.caller = caller
        self.caller_authid = caller_authid
        self.caller_authrole = caller_authrole
        self.forward_for = forward_for

        self.details = details
        self.correlation_id = correlation_id
        self.correlation_uri = correlation_uri
        self.correlation_is_anchor = correlation_is_anchor
        self.correlation_is_last = correlation_is_last

    def message_attr(self):
        """
        Returns options dict as sent within WAMP messages.
        """
        options = {}

        # note: only some attributes are actually forwarded to the WAMP CALL message, while
        # other attributes are for client-side/client-internal use only

        if self.timeout is not None:
            options[u'timeout'] = self.timeout

        if self.on_progress is not None:
            options[u'receive_progress'] = True

        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        if self.caller is not None:
            options[u'caller'] = self.caller

        if self.caller_authid is not None:
            options[u'caller_authid'] = self.caller_authid

        if self.caller_authrole is not None:
            options[u'caller_authrole'] = self.caller_authrole

        return options

    def __str__(self):
        return u"CallOptions(on_progress={}, timeout={}, caller={}, caller_authid={}, caller_authrole={}, forward_for={}, details={})".format(self.on_progress, self.timeout, self.caller, self.caller_authid, self.caller_authrole, self.forward_for, self.details)


@public
class CallResult(object):
    """
    Wrapper for remote procedure call results that contain multiple positional
    return values or keyword-based return values.
    """

    __slots__ = (
        'results',
        'kwresults',
        'enc_algo',
        'callee',
        'callee_authid',
        'callee_authrole',
        'forward_for',
    )

    def __init__(self, *results, **kwresults):
        """

        :param results: The positional result values.
        :type results: list

        :param kwresults: The keyword result values.
        :type kwresults: dict
        """
        enc_algo = kwresults.pop('enc_algo', None)
        assert(enc_algo is None or type(enc_algo) == six.text_type)

        callee = kwresults.pop('callee', None)
        callee_authid = kwresults.pop('callee_authid', None)
        callee_authrole = kwresults.pop('callee_authrole', None)

        assert callee is None or type(callee) in six.integer_types
        assert callee_authid is None or type(callee_authid) == six.text_type
        assert callee_authrole is None or type(callee_authrole) == six.text_type

        forward_for = kwresults.pop('forward_for', None)
        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        self.enc_algo = enc_algo
        self.callee = callee
        self.callee_authid = callee_authid
        self.callee_authrole = callee_authrole
        self.forward_for = forward_for
        self.results = results
        self.kwresults = kwresults

    def __str__(self):
        return u"CallResult(results={}, kwresults={}, enc_algo={}, callee={}, callee_authid={}, callee_authrole={}, forward_for={})".format(self.results, self.kwresults, self.enc_algo, self.callee, self.callee_authid, self.callee_authrole, self.forward_for)


@public
class EncodedPayload(object):
    """
    Wrapper holding an encoded application payload when using WAMP payload transparency.
    """

    __slots__ = (
        'payload',
        'enc_algo',
        'enc_serializer',
        'enc_key'
    )

    def __init__(self, payload, enc_algo, enc_serializer=None, enc_key=None):
        """

        :param payload: The encoded application payload.
        :type payload: bytes

        :param enc_algo: The payload transparency algorithm identifier to check.
        :type enc_algo: str

        :param enc_serializer: The payload transparency serializer identifier to check.
        :type enc_serializer: str

        :param enc_key: If using payload transparency with an encryption algorithm, the payload encryption key.
        :type enc_key: str or None
        """
        assert(type(payload) == six.binary_type)
        assert(type(enc_algo) == six.text_type)
        assert(enc_serializer is None or type(enc_serializer) == six.text_type)
        assert(enc_key is None or type(enc_key) == six.text_type)

        self.payload = payload
        self.enc_algo = enc_algo
        self.enc_serializer = enc_serializer
        self.enc_key = enc_key


class IPublication(object):
    """
    Represents a publication of an event. This is used with acknowledged publications.
    """

    def id(self):
        """
        The WAMP publication ID for this publication.
        """


class ISubscription(object):
    """
    Represents a subscription to a topic.
    """

    def id(self):
        """
        The WAMP subscription ID for this subscription.
        """

    def active(self):
        """
        Flag indicating if subscription is active.
        """

    def unsubscribe(self):
        """
        Unsubscribe this subscription that was previously created from
        :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`.

        After a subscription has been unsubscribed successfully, no events
        will be routed to the event handler anymore.

        Returns an instance of :tx:`twisted.internet.defer.Deferred` (when
        running on **Twisted**) or an instance of :py:class:`asyncio.Future`
        (when running on **asyncio**).

        - If the unsubscription succeeds, the returned Deferred/Future will
          *resolve* (with no return value).

        - If the unsubscription fails, the returned Deferred/Future will *reject*
          with an instance of :class:`autobahn.wamp.exception.ApplicationError`.

        :returns: A Deferred/Future for the unsubscription
        :rtype: instance(s) of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`
        """


class IRegistration(object):
    """
    Represents a registration of an endpoint.
    """

    def id(self):
        """
        The WAMP registration ID for this registration.
        """

    def active(self):
        """
        Flag indicating if registration is active.
        """

    def unregister(self):
        """
        Unregister this registration that was previously created from
        :func:`autobahn.wamp.interfaces.ICallee.register`.

        After a registration has been unregistered successfully, no calls
        will be routed to the endpoint anymore.

        Returns an instance of :tx:`twisted.internet.defer.Deferred` (when
        running on **Twisted**) or an instance of :py:class:`asyncio.Future`
        (when running on **asyncio**).

        - If the unregistration succeeds, the returned Deferred/Future will
          *resolve* (with no return value).

        - If the unregistration fails, the returned Deferred/Future will be rejected
          with an instance of :class:`autobahn.wamp.exception.ApplicationError`.

        :returns: A Deferred/Future for the unregistration
        :rtype: instance(s) of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`
        """
