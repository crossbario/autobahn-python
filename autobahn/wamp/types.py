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
from binascii import a2b_hex
from pprint import pformat
from typing import Any, Dict, List, Optional

from autobahn.util import public
from autobahn.wamp.request import Publication, Registration, Subscription

__all__ = (
    "Accept",
    "CallDetails",
    "CallOptions",
    "CallResult",
    "Challenge",
    "CloseDetails",
    "ComponentConfig",
    "Deny",
    "EncodedPayload",
    "EventDetails",
    "HelloDetails",
    "HelloReturn",
    "Publication",
    "PublishOptions",
    "RegisterOptions",
    "Registration",
    "SessionDetails",
    "SessionIdent",
    "SubscribeOptions",
    "Subscription",
    "TransportDetails",
)


@public
class ComponentConfig(object):
    """
    WAMP application component configuration. An instance of this class is
    provided to the constructor of :class:`autobahn.wamp.protocol.ApplicationSession`.
    """

    __slots__ = (
        "realm",
        "extra",
        "keyring",
        "controller",
        "shared",
        "runner",
    )

    def __init__(
        self,
        realm=None,
        extra=None,
        keyring=None,
        controller=None,
        shared=None,
        runner=None,
    ):
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
        assert realm is None or type(realm) == str
        # assert(keyring is None or ...) # FIXME

        self.realm = realm
        self.extra = extra
        self.keyring = keyring
        self.controller = controller
        self.shared = shared
        self.runner = runner

    def __str__(self):
        return "ComponentConfig(realm=<{}>, extra={}, keyring={}, controller={}, shared={}, runner={})".format(
            self.realm,
            self.extra,
            self.keyring,
            self.controller,
            self.shared,
            self.runner,
        )


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
        "realm",
        "authid",
        "authrole",
        "authmethod",
        "authprovider",
        "authextra",
    )

    def __init__(
        self,
        realm: Optional[str] = None,
        authid: Optional[str] = None,
        authrole: Optional[str] = None,
        authmethod: Optional[str] = None,
        authprovider: Optional[str] = None,
        authextra: Optional[Dict[str, Any]] = None,
    ):
        """

        :param realm: The realm the client is joined to.
        :param authid: The authentication ID the client is assigned, e.g. ``"joe"`` or ``"joe@example.com"``.
        :param authrole: The authentication role the client is assigned, e.g. ``"anonymous"``, ``"user"`` or ``"com.myapp.user"``.
        :param authmethod: The authentication method that was used to authenticate the client, e.g. ``"cookie"`` or ``"wampcra"``.
        :param authprovider: The authentication provider that was used to authenticate the client, e.g. ``"mozilla-persona"``.
        :param authextra: Application-specific authextra to be forwarded to the client in `WELCOME.details.authextra`.
        """
        assert realm is None or type(realm) == str
        assert authid is None or type(authid) == str
        assert authrole is None or type(authrole) == str
        assert authmethod is None or type(authmethod) == str
        assert authprovider is None or type(authprovider) == str
        assert authextra is None or type(authextra) == dict

        self.realm = realm
        self.authid = authid
        self.authrole = authrole
        self.authmethod = authmethod
        self.authprovider = authprovider
        self.authextra = authextra

    def __str__(self):
        return "Accept(realm=<{}>, authid=<{}>, authrole=<{}>, authmethod={}, authprovider={}, authextra={})".format(
            self.realm,
            self.authid,
            self.authrole,
            self.authmethod,
            self.authprovider,
            self.authextra,
        )


@public
class Deny(HelloReturn):
    """
    Information to deny a ``HELLO``.
    """

    __slots__ = (
        "reason",
        "message",
    )

    def __init__(self, reason="wamp.error.not_authorized", message=None):
        """

        :param reason: The reason of denying the authentication (an URI, e.g. ``'wamp.error.not_authorized'``)
        :type reason: str

        :param message: A human readable message (for logging purposes).
        :type message: str
        """
        assert type(reason) == str
        assert message is None or type(message) == str

        self.reason = reason
        self.message = message

    def __str__(self):
        return "Deny(reason=<{}>, message='{}')".format(self.reason, self.message)


@public
class Challenge(HelloReturn):
    """
    Information to challenge the client upon ``HELLO``.
    """

    __slots__ = (
        "method",
        "extra",
    )

    def __init__(self, method, extra=None):
        """

        :param method: The authentication method for the challenge (e.g. ``"wampcra"``).
        :type method: str

        :param extra: Any extra information for the authentication challenge. This is
           specific to the authentication method.
        :type extra: dict
        """
        assert type(method) == str
        assert extra is None or type(extra) == dict

        self.method = method
        self.extra = extra or {}

    def __str__(self):
        return "Challenge(method={}, extra={})".format(self.method, self.extra)


@public
class HelloDetails(object):
    """
    Provides details of a WAMP session while still attaching.
    """

    __slots__ = (
        "realm",
        "authmethods",
        "authid",
        "authrole",
        "authextra",
        "session_roles",
        "pending_session",
        "resumable",
        "resume_session",
        "resume_token",
    )

    def __init__(
        self,
        realm=None,
        authmethods=None,
        authid=None,
        authrole=None,
        authextra=None,
        session_roles=None,
        pending_session=None,
        resumable=None,
        resume_session=None,
        resume_token=None,
    ):
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
        assert realm is None or type(realm) == str
        assert authmethods is None or (
            type(authmethods) == list and all(type(x) == str for x in authmethods)
        )
        assert authid is None or type(authid) == str
        assert authrole is None or type(authrole) == str
        assert authextra is None or type(authextra) == dict
        # assert(session_roles is None or ...)  # FIXME
        assert pending_session is None or type(pending_session) == int
        assert resumable is None or type(resumable) == bool
        assert resume_session is None or type(resume_session) == int
        assert resume_token is None or type(resume_token) == str

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
        return "HelloDetails(realm=<{}>, authmethods={}, authid=<{}>, authrole=<{}>, authextra={}, session_roles={}, pending_session={}, resumable={}, resume_session={}, resume_token={})".format(
            self.realm,
            self.authmethods,
            self.authid,
            self.authrole,
            self.authextra,
            self.session_roles,
            self.pending_session,
            self.resumable,
            self.resume_session,
            self.resume_token,
        )


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
        "session",
        "authid",
        "authrole",
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
        assert session is None or type(session) == int
        assert authid is None or type(authid) == str
        assert type(authrole) == str

        self.session = session
        self.authid = authid
        self.authrole = authrole

    def __str__(self):
        return "SessionIdent(session={}, authid={}, authrole={})".format(
            self.session, self.authid, self.authrole
        )

    def marshal(self):
        obj = {
            "session": self.session,
            "authid": self.authid,
            "authrole": self.authrole,
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
            session_ident = SessionIdent(
                caller["session"], caller["authid"], caller["authrole"]
            )
        else:
            session_ident = SessionIdent(
                call_details.caller,
                call_details.caller_authid,
                call_details.caller_authrole,
            )
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
            session_ident = SessionIdent(
                publisher["session"], publisher["authid"], publisher["authrole"]
            )
        else:
            session_ident = SessionIdent(
                event_details.publisher,
                event_details.publisher_authid,
                event_details.publisher_authrole,
            )
        return session_ident


@public
class CloseDetails(object):
    """
    Provides details for a WAMP session upon close.

    .. seealso:: :meth:`autobahn.wamp.interfaces.ISession.onLeave`
    """

    REASON_DEFAULT = "wamp.close.normal"
    REASON_TRANSPORT_LOST = "wamp.close.transport_lost"

    __slots__ = (
        "reason",
        "message",
    )

    def __init__(self, reason=None, message=None):
        """

        :param reason: The close reason (an URI, e.g. ``wamp.close.normal``)
        :type reason: str

        :param message: Closing log message.
        :type message: str
        """
        assert reason is None or type(reason) == str
        assert message is None or type(message) == str

        self.reason = reason
        self.message = message

    def marshal(self):
        obj = {"reason": self.reason, "message": self.message}
        return obj

    def __str__(self):
        return "CloseDetails(reason=<{}>, message='{}')".format(
            self.reason, self.message
        )


@public
class SubscribeOptions(object):
    """
    Used to provide options for subscribing in
    :meth:`autobahn.wamp.interfaces.ISubscriber.subscribe`.
    """

    __slots__ = (
        "match",
        "details",
        "details_arg",
        "get_retained",
        "forward_for",
        "correlation_id",
        "correlation_uri",
        "correlation_is_anchor",
        "correlation_is_last",
    )

    def __init__(
        self,
        match=None,
        details=None,
        details_arg=None,
        forward_for=None,
        get_retained=None,
        correlation_id=None,
        correlation_uri=None,
        correlation_is_anchor=None,
        correlation_is_last=None,
    ):
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
        assert match is None or (
            type(match) == str and match in ["exact", "prefix", "wildcard"]
        )
        assert details is None or (type(details) == bool and details_arg is None)
        assert (
            details_arg is None or type(details_arg) == str
        )  # yes, "str" is correct here, since this is about Python identifiers!
        assert get_retained is None or type(get_retained) is bool

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        self.match = match

        # FIXME: this is for backwards compat, but we'll deprecate it in the future
        self.details = details
        if details:
            self.details_arg = "details"
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
            options["match"] = self.match

        if self.get_retained is not None:
            options["get_retained"] = self.get_retained

        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        return options

    def __str__(self):
        return "SubscribeOptions(match={}, details={}, details_arg={}, get_retained={}, forward_for={})".format(
            self.match,
            self.details,
            self.details_arg,
            self.get_retained,
            self.forward_for,
        )


@public
class EventDetails(object):
    """
    Provides details on an event when calling an event handler
    previously registered.
    """

    __slots__ = (
        "subscription",
        "publication",
        "publisher",
        "publisher_authid",
        "publisher_authrole",
        "topic",
        "retained",
        "transaction_hash",
        "enc_algo",
        "forward_for",
    )

    def __init__(
        self,
        subscription,
        publication,
        publisher=None,
        publisher_authid=None,
        publisher_authrole=None,
        topic=None,
        retained=None,
        transaction_hash=None,
        enc_algo=None,
        forward_for=None,
    ):
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
            was in use (currently, either ``None`` or ``'cryptobox'``).
        :type enc_algo: str or None

        :param transaction_hash: An application provided transaction hash for the originating call, which may
            be used in the router to throttle or deduplicate the calls on the procedure. See the discussion
            `here <https://github.com/wamp-proto/wamp-proto/issues/391#issuecomment-998577967>`_.
        :type transaction_hash: str

        :param forward_for: When this Event is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert isinstance(subscription, Subscription)
        assert type(publication) == int
        assert publisher is None or type(publisher) == int
        assert publisher_authid is None or type(publisher_authid) == str
        assert publisher_authrole is None or type(publisher_authrole) == str
        assert topic is None or type(topic) == str
        assert retained is None or type(retained) is bool
        assert transaction_hash is None or type(transaction_hash) == str
        assert enc_algo is None or type(enc_algo) == str
        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        self.subscription = subscription
        self.publication = publication
        self.publisher = publisher
        self.publisher_authid = publisher_authid
        self.publisher_authrole = publisher_authrole
        self.topic = topic
        self.retained = retained
        self.transaction_hash = transaction_hash
        self.enc_algo = enc_algo
        self.forward_for = forward_for

    def __str__(self):
        return "EventDetails(subscription={}, publication={}, publisher={}, publisher_authid={}, publisher_authrole={}, topic=<{}>, retained={}, transaction_hash={}, enc_algo={}, forward_for={})".format(
            self.subscription,
            self.publication,
            self.publisher,
            self.publisher_authid,
            self.publisher_authrole,
            self.topic,
            self.retained,
            self.transaction_hash,
            self.enc_algo,
            self.forward_for,
        )


@public
class PublishOptions(object):
    """
    Used to provide options for subscribing in
    :meth:`autobahn.wamp.interfaces.IPublisher.publish`.
    """

    __slots__ = (
        "acknowledge",
        "exclude_me",
        "exclude",
        "exclude_authid",
        "exclude_authrole",
        "eligible",
        "eligible_authid",
        "eligible_authrole",
        "retain",
        "transaction_hash",
        "forward_for",
        "correlation_id",
        "correlation_uri",
        "correlation_is_anchor",
        "correlation_is_last",
    )

    def __init__(
        self,
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
        transaction_hash=None,
        correlation_id=None,
        correlation_uri=None,
        correlation_is_anchor=None,
        correlation_is_last=None,
    ):
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

        :param transaction_hash: An application provided transaction hash for the published event, which may
            be used in the router to throttle or deduplicate the events on the topic. See the discussion
            `here <https://github.com/wamp-proto/wamp-proto/issues/391#issuecomment-998577967>`_.
        :type transaction_hash: str

        :param forward_for: When this Event is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert acknowledge is None or type(acknowledge) == bool
        assert exclude_me is None or type(exclude_me) == bool
        assert (
            exclude is None
            or type(exclude) == int
            or (type(exclude) == list and all(type(x) == int for x in exclude))
        )
        assert (
            exclude_authid is None
            or type(exclude_authid) == str
            or (
                type(exclude_authid) == list
                and all(type(x) == str for x in exclude_authid)
            )
        )
        assert (
            exclude_authrole is None
            or type(exclude_authrole) == str
            or (
                type(exclude_authrole) == list
                and all(type(x) == str for x in exclude_authrole)
            )
        )
        assert (
            eligible is None
            or type(eligible) == int
            or (type(eligible) == list and all(type(x) == int for x in eligible))
        )
        assert (
            eligible_authid is None
            or type(eligible_authid) == str
            or (
                type(eligible_authid) == list
                and all(type(x) == str for x in eligible_authid)
            )
        )
        assert (
            eligible_authrole is None
            or type(eligible_authrole) == str
            or (
                type(eligible_authrole) == list
                and all(type(x) == str for x in eligible_authrole)
            )
        )
        assert retain is None or type(retain) == bool
        assert transaction_hash is None or type(transaction_hash) == str

        assert forward_for is None or type(forward_for) == list, (
            "forward_for, when present, must have list type - was {}".format(
                type(forward_for)
            )
        )
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict, (
                    "forward_for must be type dict - was {}".format(type(ff))
                )
                assert "session" in ff, "forward_for must have session attribute"
                assert type(ff["session"]) == int, (
                    "forward_for.session must have integer type - was {}".format(
                        type(ff["session"])
                    )
                )
                assert "authid" in ff, "forward_for must have authid attributed"
                assert type(ff["authid"]) == str, (
                    "forward_for.authid must have str type - was {}".format(
                        type(ff["authid"])
                    )
                )
                assert "authrole" in ff, "forward_for must have authrole attribute"
                assert type(ff["authrole"]) == str, (
                    "forward_for.authrole must have str type - was {}".format(
                        type(ff["authrole"])
                    )
                )

        self.acknowledge = acknowledge
        self.exclude_me = exclude_me
        self.exclude = exclude
        self.exclude_authid = exclude_authid
        self.exclude_authrole = exclude_authrole
        self.eligible = eligible
        self.eligible_authid = eligible_authid
        self.eligible_authrole = eligible_authrole
        self.retain = retain
        self.transaction_hash = transaction_hash
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
            options["acknowledge"] = self.acknowledge

        if self.exclude_me is not None:
            options["exclude_me"] = self.exclude_me

        if self.exclude is not None:
            options["exclude"] = (
                self.exclude if type(self.exclude) == list else [self.exclude]
            )

        if self.exclude_authid is not None:
            options["exclude_authid"] = (
                self.exclude_authid
                if type(self.exclude_authid) == list
                else [self.exclude_authid]
            )

        if self.exclude_authrole is not None:
            options["exclude_authrole"] = (
                self.exclude_authrole
                if type(self.exclude_authrole) == list
                else [self.exclude_authrole]
            )

        if self.eligible is not None:
            options["eligible"] = (
                self.eligible if type(self.eligible) == list else [self.eligible]
            )

        if self.eligible_authid is not None:
            options["eligible_authid"] = (
                self.eligible_authid
                if type(self.eligible_authid) == list
                else [self.eligible_authid]
            )

        if self.eligible_authrole is not None:
            options["eligible_authrole"] = (
                self.eligible_authrole
                if type(self.eligible_authrole) == list
                else [self.eligible_authrole]
            )

        if self.retain is not None:
            options["retain"] = self.retain

        if self.transaction_hash is not None:
            options["transaction_hash"] = self.transaction_hash

        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        return options

    def __str__(self):
        return "PublishOptions(acknowledge={}, exclude_me={}, exclude={}, exclude_authid={}, exclude_authrole={}, eligible={}, eligible_authid={}, eligible_authrole={}, retain={}, transaction_hash={}, forward_for={})".format(
            self.acknowledge,
            self.exclude_me,
            self.exclude,
            self.exclude_authid,
            self.exclude_authrole,
            self.eligible,
            self.eligible_authid,
            self.eligible_authrole,
            self.retain,
            self.transaction_hash,
            self.forward_for,
        )


@public
class RegisterOptions(object):
    """
    Used to provide options for registering in
    :meth:`autobahn.wamp.interfaces.ICallee.register`.
    """

    __slots__ = (
        "match",
        "invoke",
        "concurrency",
        "force_reregister",
        "forward_for",
        "details",
        "details_arg",
        "correlation_id",
        "correlation_uri",
        "correlation_is_anchor",
        "correlation_is_last",
    )

    def __init__(
        self,
        match=None,
        invoke=None,
        concurrency=None,
        force_reregister=None,
        forward_for=None,
        details=None,
        details_arg=None,
        correlation_id=None,
        correlation_uri=None,
        correlation_is_anchor=None,
        correlation_is_last=None,
    ):
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
        assert match is None or (
            type(match) == str and match in ["exact", "prefix", "wildcard"]
        )
        assert invoke is None or (
            type(invoke) == str
            and invoke in ["single", "first", "last", "roundrobin", "random"]
        )
        assert concurrency is None or (type(concurrency) == int and concurrency > 0)
        assert details is None or (type(details) == bool and details_arg is None)
        assert (
            details_arg is None or type(details_arg) == str
        )  # yes, "str" is correct here, since this is about Python identifiers!
        assert force_reregister in [None, True, False]

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        self.match = match
        self.invoke = invoke
        self.concurrency = concurrency
        self.force_reregister = force_reregister
        self.forward_for = forward_for

        # FIXME: this is for backwards compat, but we'll deprecate it in the future
        self.details = details
        if details:
            self.details_arg = "details"
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
            options["match"] = self.match

        if self.invoke is not None:
            options["invoke"] = self.invoke

        if self.concurrency is not None:
            options["concurrency"] = self.concurrency

        if self.force_reregister is not None:
            options["force_reregister"] = self.force_reregister

        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        return options

    def __str__(self):
        return "RegisterOptions(match={}, invoke={}, concurrency={}, details={}, details_arg={}, force_reregister={}, forward_for={})".format(
            self.match,
            self.invoke,
            self.concurrency,
            self.details,
            self.details_arg,
            self.force_reregister,
            self.forward_for,
        )


@public
class CallDetails(object):
    """
    Provides details on a call when an endpoint previously
    registered is being called and opted to receive call details.
    """

    __slots__ = (
        "registration",
        "progress",
        "caller",
        "caller_authid",
        "caller_authrole",
        "procedure",
        "transaction_hash",
        "enc_algo",
        "forward_for",
    )

    def __init__(
        self,
        registration,
        progress=None,
        caller=None,
        caller_authid=None,
        caller_authrole=None,
        procedure=None,
        transaction_hash=None,
        enc_algo=None,
        forward_for=None,
    ):
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
        assert isinstance(registration, Registration)
        assert progress is None or callable(progress)
        assert caller is None or type(caller) == int
        assert caller_authid is None or type(caller_authid) == str
        assert caller_authrole is None or type(caller_authrole) == str
        assert procedure is None or type(procedure) == str
        assert transaction_hash is None or type(transaction_hash) == str
        assert enc_algo is None or type(enc_algo) == str

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        self.registration = registration
        self.progress = progress
        self.caller = caller
        self.caller_authid = caller_authid
        self.caller_authrole = caller_authrole
        self.procedure = procedure
        self.transaction_hash = transaction_hash
        self.enc_algo = enc_algo
        self.forward_for = forward_for

    def __str__(self):
        return "CallDetails(registration={}, progress={}, caller={}, caller_authid={}, caller_authrole={}, procedure=<{}>, transaction_hash={}, enc_algo={}, forward_for={})".format(
            self.registration,
            self.progress,
            self.caller,
            self.caller_authid,
            self.caller_authrole,
            self.procedure,
            self.transaction_hash,
            self.enc_algo,
            self.forward_for,
        )


@public
class CallOptions(object):
    """
    Used to provide options for calling with :meth:`autobahn.wamp.interfaces.ICaller.call`.
    """

    __slots__ = (
        "on_progress",
        "timeout",
        "transaction_hash",
        "caller",
        "caller_authid",
        "caller_authrole",
        "forward_for",
        "correlation_id",
        "correlation_uri",
        "correlation_is_anchor",
        "correlation_is_last",
        "details",
    )

    def __init__(
        self,
        on_progress=None,
        timeout=None,
        transaction_hash=None,
        caller=None,
        caller_authid=None,
        caller_authrole=None,
        forward_for=None,
        correlation_id=None,
        correlation_uri=None,
        correlation_is_anchor=None,
        correlation_is_last=None,
        details=None,
    ):
        """

        :param on_progress: A callback that will be called when the remote endpoint
           called yields interim call progress results.
        :type on_progress: callable

        :param timeout: Time in seconds after which the call should be automatically canceled.
        :type timeout: float

        :param transaction_hash: An application provided transaction hash for the originating call, which may
            be used in the router to throttle or deduplicate the calls on the procedure. See the discussion
            `here <https://github.com/wamp-proto/wamp-proto/issues/391#issuecomment-998577967>`_.
        :type transaction_hash: str

        :param forward_for: When this Call is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert on_progress is None or callable(on_progress)
        assert timeout is None or (
            type(timeout) in list((int,)) + [float] and timeout > 0
        )
        assert transaction_hash is None or type(transaction_hash) == str
        assert details is None or type(details) == bool
        assert caller is None or type(caller) == int
        assert caller_authid is None or type(caller_authid) == str
        assert caller_authrole is None or type(caller_authrole) == str
        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        self.on_progress = on_progress
        self.timeout = timeout
        self.transaction_hash = transaction_hash

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
            options["timeout"] = self.timeout

        if self.on_progress is not None:
            options["receive_progress"] = True

        if self.transaction_hash is not None:
            options["transaction_hash"] = self.transaction_hash

        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        if self.caller is not None:
            options["caller"] = self.caller

        if self.caller_authid is not None:
            options["caller_authid"] = self.caller_authid

        if self.caller_authrole is not None:
            options["caller_authrole"] = self.caller_authrole

        return options

    def __str__(self):
        return "CallOptions(on_progress={}, timeout={}, transaction_hash={}, caller={}, caller_authid={}, caller_authrole={}, forward_for={}, details={})".format(
            self.on_progress,
            self.timeout,
            self.transaction_hash,
            self.caller,
            self.caller_authid,
            self.caller_authrole,
            self.forward_for,
            self.details,
        )


@public
class CallResult(object):
    """
    Wrapper for remote procedure call results that contain multiple positional
    return values or keyword-based return values.
    """

    __slots__ = (
        "results",
        "kwresults",
        "enc_algo",
        "callee",
        "callee_authid",
        "callee_authrole",
        "forward_for",
    )

    def __init__(self, *results, **kwresults):
        """

        :param results: The positional result values.
        :type results: list

        :param kwresults: The keyword result values.
        :type kwresults: dict
        """
        enc_algo = kwresults.pop("enc_algo", None)
        assert enc_algo is None or type(enc_algo) == str

        callee = kwresults.pop("callee", None)
        callee_authid = kwresults.pop("callee_authid", None)
        callee_authrole = kwresults.pop("callee_authrole", None)

        assert callee is None or type(callee) == int
        assert callee_authid is None or type(callee_authid) == str
        assert callee_authrole is None or type(callee_authrole) == str

        forward_for = kwresults.pop("forward_for", None)
        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        self.enc_algo = enc_algo
        self.callee = callee
        self.callee_authid = callee_authid
        self.callee_authrole = callee_authrole
        self.forward_for = forward_for
        self.results = results
        self.kwresults = kwresults

    def __str__(self):
        return "CallResult(results={}, kwresults={}, enc_algo={}, callee={}, callee_authid={}, callee_authrole={}, forward_for={})".format(
            self.results,
            self.kwresults,
            self.enc_algo,
            self.callee,
            self.callee_authid,
            self.callee_authrole,
            self.forward_for,
        )


@public
class EncodedPayload(object):
    """
    Wrapper holding an encoded application payload when using WAMP payload transparency.
    """

    __slots__ = ("payload", "enc_algo", "enc_serializer", "enc_key")

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
        assert type(payload) == bytes
        assert type(enc_algo) == str
        assert enc_serializer is None or type(enc_serializer) == str
        assert enc_key is None or type(enc_key) == str

        self.payload = payload
        self.enc_algo = enc_algo
        self.enc_serializer = enc_serializer
        self.enc_key = enc_key


@public
class IPublication(object):
    """
    Represents a publication of an event. This is used with acknowledged publications.
    """

    def id(self):
        """
        The WAMP publication ID for this publication.
        """


@public
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
        :meth:`autobahn.wamp.interfaces.ISubscriber.subscribe`.

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


@public
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
        :meth:`autobahn.wamp.interfaces.ICallee.register`.

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


@public
class TransportDetails(object):
    """
    Details about a WAMP transport used for carrying a WAMP session. WAMP can be communicated
    over different bidirectional underlying transport mechanisms, such as TCP, TLS, Serial
    connections or In-memory queues.
    """

    __slots__ = (
        "_channel_type",
        "_channel_framing",
        "_channel_serializer",
        "_own",
        "_peer",
        "_is_server",
        "_own_pid",
        "_own_tid",
        "_own_fd",
        "_is_secure",
        "_channel_id",
        "_peer_cert",
        "_websocket_protocol",
        "_websocket_extensions_in_use",
        "_http_headers_received",
        "_http_headers_sent",
        "_http_cbtid",
    )

    CHANNEL_TYPE_NONE = 0
    CHANNEL_TYPE_FUNCTION = 1
    CHANNEL_TYPE_MEMORY = 2
    CHANNEL_TYPE_SERIAL = 3
    CHANNEL_TYPE_TCP = 4
    CHANNEL_TYPE_TLS = 5
    CHANNEL_TYPE_UDP = 6
    CHANNEL_TYPE_DTLS = 7

    CHANNEL_TYPE_TO_STR = {
        CHANNEL_TYPE_NONE: "null",
        CHANNEL_TYPE_FUNCTION: "function",
        CHANNEL_TYPE_MEMORY: "memory",
        CHANNEL_TYPE_SERIAL: "serial",
        CHANNEL_TYPE_TCP: "tcp",
        CHANNEL_TYPE_TLS: "tls",
        CHANNEL_TYPE_UDP: "udp",
        CHANNEL_TYPE_DTLS: "dtls",
    }

    CHANNEL_TYPE_FROM_STR = {
        "null": CHANNEL_TYPE_NONE,
        # for same process, function-call based transports of WAMP,
        # e.g. in router embedded WAMP sessions
        "function": CHANNEL_TYPE_FUNCTION,
        # for Unix domain sockets and pipes (IPC)
        "memory": CHANNEL_TYPE_MEMORY,
        # for Serial ports to wired devices
        "serial": CHANNEL_TYPE_SERIAL,
        # for plain, unencrypted TCPv4/TCPv6 connections, most commonly over
        # "real" network connections (incl. loopback)
        "tcp": CHANNEL_TYPE_TCP,
        # for TLS encrypted TCPv4/TCPv6 connections
        "tls": CHANNEL_TYPE_TLS,
        # for plain, unencrypted UDPv4/UDPv6 datagram transports of WAMP (future!)
        "udp": CHANNEL_TYPE_UDP,
        # for DTLS encrypted UDPv6 datagram transports of WAMP (future!)
        "dtls": CHANNEL_TYPE_DTLS,
    }

    CHANNEL_FRAMING_NONE = 0
    CHANNEL_FRAMING_NATIVE = 1
    CHANNEL_FRAMING_WEBSOCKET = 2
    CHANNEL_FRAMING_RAWSOCKET = 3

    CHANNEL_FRAMING_TO_STR = {
        CHANNEL_FRAMING_NONE: "null",
        CHANNEL_FRAMING_NATIVE: "native",
        CHANNEL_FRAMING_WEBSOCKET: "websocket",
        CHANNEL_FRAMING_RAWSOCKET: "rawsocket",
    }

    CHANNEL_FRAMING_FROM_STR = {
        "null": CHANNEL_TYPE_NONE,
        "native": CHANNEL_FRAMING_NATIVE,
        "websocket": CHANNEL_FRAMING_WEBSOCKET,
        "rawsocket": CHANNEL_FRAMING_RAWSOCKET,
    }

    # Keep in sync with Serializer.SERIALIZER_ID and Serializer.RAWSOCKET_SERIALIZER_ID
    CHANNEL_SERIALIZER_NONE = 0
    CHANNEL_SERIALIZER_JSON = 1
    CHANNEL_SERIALIZER_MSGPACK = 2
    CHANNEL_SERIALIZER_CBOR = 3
    CHANNEL_SERIALIZER_UBJSON = 4
    CHANNEL_SERIALIZER_FLATBUFFERS = 5

    CHANNEL_SERIALIZER_TO_STR = {
        CHANNEL_SERIALIZER_NONE: "null",
        CHANNEL_SERIALIZER_JSON: "json",
        CHANNEL_SERIALIZER_MSGPACK: "msgpack",
        CHANNEL_SERIALIZER_CBOR: "cbor",
        CHANNEL_SERIALIZER_UBJSON: "ubjson",
        CHANNEL_SERIALIZER_FLATBUFFERS: "flatbuffers",
    }

    CHANNEL_SERIALIZER_FROM_STR = {
        "null": CHANNEL_SERIALIZER_NONE,
        "json": CHANNEL_SERIALIZER_JSON,
        "msgpack": CHANNEL_SERIALIZER_MSGPACK,
        "cbor": CHANNEL_SERIALIZER_CBOR,
        "ubjson": CHANNEL_SERIALIZER_UBJSON,
        "flatbuffers": CHANNEL_SERIALIZER_FLATBUFFERS,
    }

    def __init__(
        self,
        channel_type: Optional[int] = None,
        channel_framing: Optional[int] = None,
        channel_serializer: Optional[int] = None,
        own: Optional[str] = None,
        peer: Optional[str] = None,
        is_server: Optional[bool] = None,
        own_pid: Optional[int] = None,
        own_tid: Optional[int] = None,
        own_fd: Optional[int] = None,
        is_secure: Optional[bool] = None,
        channel_id: Optional[Dict[str, bytes]] = None,
        peer_cert: Optional[Dict[str, Any]] = None,
        websocket_protocol: Optional[str] = None,
        websocket_extensions_in_use: Optional[List[str]] = None,
        http_headers_received: Optional[Dict[str, Any]] = None,
        http_headers_sent: Optional[Dict[str, Any]] = None,
        http_cbtid: Optional[str] = None,
    ):
        self._channel_type = channel_type
        self._channel_framing = channel_framing
        self._channel_serializer = channel_serializer
        self._own = own
        self._peer = peer
        self._is_server = is_server
        self._own_pid = own_pid
        self._own_tid = own_tid
        self._own_fd = own_fd
        self._is_secure = is_secure
        self._channel_id = channel_id
        self._peer_cert = peer_cert
        self._websocket_protocol = websocket_protocol
        self._websocket_extensions_in_use = websocket_extensions_in_use
        self._http_headers_received = http_headers_received
        self._http_headers_sent = http_headers_sent
        self._http_cbtid = http_cbtid

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if other._channel_type != self._channel_type:
            return False
        if other._channel_framing != self._channel_framing:
            return False
        if other._channel_serializer != self._channel_serializer:
            return False
        if other._own != self._own:
            return False
        if other._peer != self._peer:
            return False
        if other._is_server != self._is_server:
            return False
        if other._own_pid != self._own_pid:
            return False
        if other._own_tid != self._own_tid:
            return False
        if other._own_fd != self._own_fd:
            return False
        if other._is_secure != self._is_secure:
            return False
        if other._channel_id != self._channel_id:
            return False
        if other._peer_cert != self._peer_cert:
            return False
        if other._websocket_protocol != self._websocket_protocol:
            return False
        if other._websocket_extensions_in_use != self._websocket_extensions_in_use:
            return False
        if other._http_headers_received != self._http_headers_received:
            return False
        if other._http_headers_sent != self._http_headers_sent:
            return False
        if other._http_cbtid != self._http_cbtid:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def parse(data: Dict[str, Any]) -> "TransportDetails":
        assert type(data) == dict

        obj = TransportDetails()
        if "channel_type" in data and data["channel_type"] is not None:
            if (
                type(data["channel_type"]) != str
                or data["channel_type"] not in TransportDetails.CHANNEL_TYPE_FROM_STR
            ):
                raise ValueError(
                    'invalid "channel_type", was type {} (value {})'.format(
                        type(data["channel_type"]), data["channel_type"]
                    )
                )
            obj.channel_type = TransportDetails.CHANNEL_TYPE_FROM_STR[
                data["channel_type"]
            ]
        if "channel_framing" in data and data["channel_framing"] is not None:
            if (
                type(data["channel_framing"]) != str
                or data["channel_framing"]
                not in TransportDetails.CHANNEL_FRAMING_FROM_STR
            ):
                raise ValueError(
                    'invalid "channel_framing", was type {} (value {})'.format(
                        type(data["channel_framing"]), data["channel_framing"]
                    )
                )
            obj.channel_framing = TransportDetails.CHANNEL_FRAMING_FROM_STR[
                data["channel_framing"]
            ]
        if "channel_serializer" in data and data["channel_serializer"] is not None:
            if (
                type(data["channel_serializer"]) != str
                or data["channel_serializer"]
                not in TransportDetails.CHANNEL_SERIALIZER_FROM_STR
            ):
                raise ValueError(
                    'invalid "channel_serializer", was type {} (value {})'.format(
                        type(data["channel_serializer"]), data["channel_serializer"]
                    )
                )
            obj.channel_serializer = TransportDetails.CHANNEL_SERIALIZER_FROM_STR[
                data["channel_serializer"]
            ]
        if "own" in data and data["own"] is not None:
            if type(data["own"]) != str:
                raise ValueError(
                    '"own" must be a string, was {}'.format(type(data["own"]))
                )
            obj.own = data["own"]
        if "peer" in data and data["peer"] is not None:
            if type(data["peer"]) != str:
                raise ValueError(
                    '"peer" must be a string, was {}'.format(type(data["peer"]))
                )
            obj.peer = data["peer"]
        if "is_server" in data and data["is_server"] is not None:
            if type(data["is_server"]) != bool:
                raise ValueError(
                    '"is_server" must be a bool, was {}'.format(type(data["is_server"]))
                )
            obj.is_server = data["is_server"]
        if "own_pid" in data and data["own_pid"] is not None:
            if type(data["own_pid"]) != int:
                raise ValueError(
                    '"own_pid" must be an int, was {}'.format(type(data["own_pid"]))
                )
            obj.own_pid = data["own_pid"]
        if "own_tid" in data and data["own_tid"] is not None:
            if type(data["own_tid"]) != int:
                raise ValueError(
                    '"own_tid" must be an int, was {}'.format(type(data["own_tid"]))
                )
            obj.own_tid = data["own_tid"]
        if "own_fd" in data and data["own_fd"] is not None:
            if type(data["own_fd"]) != int:
                raise ValueError(
                    '"own_fd" must be an int, was {}'.format(type(data["own_fd"]))
                )
            obj.own_fd = data["own_fd"]
        if "is_secure" in data and data["is_secure"] is not None:
            if type(data["is_secure"]) != bool:
                raise ValueError(
                    '"is_secure" must be a bool, was {}'.format(type(data["is_secure"]))
                )
            obj.is_secure = data["is_secure"]
        if "channel_id" in data and data["channel_id"] is not None:
            if type(data["channel_id"]) != dict:
                raise ValueError(
                    '"channel_id" must be a dict, was {}'.format(
                        type(data["channel_id"])
                    )
                )
            channel_id = {}
            for binding_type in data["channel_id"]:
                if binding_type not in ["tls-unique"]:
                    raise ValueError(
                        'invalid binding type "{}" in "channel_id" map'.format(
                            binding_type
                        )
                    )
                binding_id_hex = data["channel_id"][binding_type]
                if type(binding_id_hex) != str or len(binding_id_hex) != 64:
                    raise ValueError(
                        'invalid binding ID "{}" in "channel_id" map'.format(
                            binding_id_hex
                        )
                    )
                binding_id = a2b_hex(binding_id_hex)
                channel_id[binding_type] = binding_id
            obj.channel_id = channel_id
        if "websocket_protocol" in data and data["websocket_protocol"] is not None:
            if type(data["websocket_protocol"]) != str:
                raise ValueError(
                    '"websocket_protocol" must be a string, was {}'.format(
                        type(data["websocket_protocol"])
                    )
                )
            obj.websocket_protocol = data["websocket_protocol"]
        if (
            "websocket_extensions_in_use" in data
            and data["websocket_extensions_in_use"] is not None
        ):
            if type(data["websocket_extensions_in_use"]) != list:
                raise ValueError(
                    '"websocket_extensions_in_use" must be a list of strings, was {}'.format(
                        type(data["websocket_extensions_in_use"])
                    )
                )
            obj.websocket_extensions_in_use = data["websocket_extensions_in_use"]
        if (
            "http_headers_received" in data
            and data["http_headers_received"] is not None
        ):
            if type(data["http_headers_received"]) != dict:
                raise ValueError(
                    '"http_headers_received" must be a map of strings, was {}'.format(
                        type(data["http_headers_received"])
                    )
                )
            obj.http_headers_received = data["http_headers_received"]
        if "http_headers_sent" in data and data["http_headers_sent"] is not None:
            if type(data["http_headers_sent"]) != dict:
                raise ValueError(
                    '"http_headers_sent" must be a map of strings, was {}'.format(
                        type(data["http_headers_sent"])
                    )
                )
            obj.http_headers_sent = data["http_headers_sent"]
        if "http_cbtid" in data and data["http_cbtid"] is not None:
            if type(data["http_cbtid"]) != str:
                raise ValueError(
                    '"http_cbtid" must be a string, was {}'.format(
                        type(data["http_cbtid"])
                    )
                )
            obj.http_cbtid = data["http_cbtid"]
        return obj

    def marshal(self) -> Dict[str, Any]:
        return {
            "channel_type": self.CHANNEL_TYPE_TO_STR.get(self._channel_type, None),
            "channel_framing": self.CHANNEL_FRAMING_TO_STR.get(
                self._channel_framing, None
            ),
            "channel_serializer": self.CHANNEL_SERIALIZER_TO_STR.get(
                self._channel_serializer, None
            ),
            "own": self._own,
            "peer": self._peer,
            "is_server": self._is_server,
            "own_pid": self._own_pid,
            "own_tid": self._own_tid,
            "own_fd": self._own_fd,
            "is_secure": self._is_secure,
            "channel_id": self._channel_id,
            "peer_cert": self._peer_cert,
            "websocket_protocol": self._websocket_protocol,
            "websocket_extensions_in_use": self._websocket_extensions_in_use,
            "http_headers_received": self._http_headers_received,
            "http_headers_sent": self._http_headers_sent,
            "http_cbtid": self._http_cbtid,
        }

    def __str__(self) -> str:
        return pformat(self.marshal())

    @property
    def channel_typeid(self):
        """
        Return a short type identifier string for the combination transport type, framing
        and serializer. Here are some common examples:

        * ``"tcp-websocket-json"``
        * ``"tls-websocket-msgpack"``
        * ``"memory-rawsocket-cbor"``
        * ``"memory-rawsocket-flatbuffers"``
        * ``"function-native-native"``

        :return:
        """
        return "{}-{}-{}".format(
            self.CHANNEL_TYPE_TO_STR[self.channel_type or 0],
            self.CHANNEL_FRAMING_TO_STR[self.channel_framing or 0],
            self.CHANNEL_SERIALIZER_TO_STR[self.channel_serializer or 0],
        )

    @property
    def channel_type(self) -> Optional[int]:
        """
        The underlying transport type, e.g. TCP.
        """
        return self._channel_type

    @channel_type.setter
    def channel_type(self, value: Optional[int]):
        self._channel_type = value

    @property
    def channel_framing(self) -> Optional[int]:
        """
        The message framing used on this transport, e.g. WebSocket.
        """
        return self._channel_framing

    @channel_framing.setter
    def channel_framing(self, value: Optional[int]):
        self._channel_framing = value

    @property
    def channel_serializer(self) -> Optional[int]:
        """
        The message serializer used on this transport, e.g. CBOR (batched or unbatched).
        """
        return self._channel_serializer

    @channel_serializer.setter
    def channel_serializer(self, value: Optional[int]):
        self._channel_serializer = value

    @property
    def own(self) -> Optional[str]:
        """

        https://github.com/crossbario/autobahn-python/blob/master/autobahn/websocket/test/test_websocket_url.py
        https://github.com/crossbario/autobahn-python/blob/master/autobahn/rawsocket/test/test_rawsocket_url.py

        A WebSocket server URL:

        * ``ws://localhost``
        * ``wss://example.com:443/ws``
        * ``ws://62.146.25.34:80/ws``
        * ``wss://localhost:9090/ws?foo=bar``

        A RawSocket server URL:

        * ``rs://crossbar:8081``
        * ``rss://example.com``
        * ``rs://unix:/tmp/file.sock``
        * ``rss://unix:../file.sock``
        """
        return self._own

    @own.setter
    def own(self, value: Optional[str]):
        self._own = value

    @property
    def peer(self) -> Optional[str]:
        """
        The peer this transport is connected to.

        process:12784
        pipe

        tcp4:127.0.0.1:38810
        tcp4:127.0.0.1:8080
        unix:/tmp/file.sock

        """
        return self._peer

    @peer.setter
    def peer(self, value: Optional[str]):
        self._peer = value

    @property
    def is_server(self) -> Optional[bool]:
        """
        Flag indicating whether this side of the peer is a "server" (on underlying transports that
            follows a client-server approach).
        """
        return self._is_server

    @is_server.setter
    def is_server(self, value: Optional[bool]):
        self._is_server = value

    @property
    def own_pid(self) -> Optional[int]:
        """
        The process ID (PID) of this end of the connection.
        """
        return self._own_pid

    @own_pid.setter
    def own_pid(self, value: Optional[int]):
        self._own_pid = value

    @property
    def own_tid(self) -> Optional[int]:
        """
        The native thread ID of this end of the connection.

        See https://docs.python.org/3/library/threading.html#threading.get_native_id.

        .. note::

            On CPython 3.7, instead of the native thread ID, a synthetic thread ID that has no direct meaning
            is used (via ``threading.get_ident()``).
        """
        return self._own_tid

    @own_tid.setter
    def own_tid(self, value: Optional[int]):
        self._own_tid = value

    @property
    def own_fd(self) -> Optional[int]:
        """
        The file descriptor (FD) at this end of the connection.
        """
        return self._own_fd

    @own_fd.setter
    def own_fd(self, value: Optional[int]):
        self._own_fd = value

    @property
    def is_secure(self) -> Optional[bool]:
        """
        Flag indicating whether this transport runs over TLS (or similar), and hence is encrypting at
        the byte stream or datagram transport level (beneath WAMP payload encryption).
        """
        return self._is_secure

    @is_secure.setter
    def is_secure(self, value: Optional[bool]):
        self._is_secure = value

    @property
    def channel_id(self) -> Dict[str, bytes]:
        """
        If this transport runs over a secure underlying connection, e.g. TLS,
        return a map of channel binding by binding type.

        Return the unique channel ID of the underlying transport. This is used to
        mitigate credential forwarding man-in-the-middle attacks when running
        application level authentication (eg WAMP-cryptosign) which are decoupled
        from the underlying transport.

        The channel ID is only available when running over TLS (either WAMP-WebSocket
        or WAMP-RawSocket). It is not available for non-TLS transports (plain TCP or
        Unix domain sockets). It is also not available for WAMP-over-HTTP/Longpoll.
        Further, it is currently unimplemented for asyncio (only works on Twisted).

        The channel ID is computed as follows:

           - for a client, the SHA256 over the "TLS Finished" message sent by the client
             to the server is returned.

           - for a server, the SHA256 over the "TLS Finished" message the server expected
             the client to send

        Note: this is similar to `tls-unique` as described in RFC5929, but instead
        of returning the raw "TLS Finished" message, it returns a SHA256 over such a
        message. The reason is that we use the channel ID mainly with WAMP-cryptosign,
        which is based on Ed25519, where keys are always 32 bytes. And having a channel ID
        which is always 32 bytes (independent of the TLS ciphers/hashfuns in use) allows
        use to easily XOR channel IDs with Ed25519 keys and WAMP-cryptosign challenges.

        WARNING: For safe use of this (that is, for safely binding app level authentication
        to the underlying transport), you MUST use TLS, and you SHOULD deactivate both
        TLS session renegotiation and TLS session resumption.

        References:

           - https://tools.ietf.org/html/rfc5056
           - https://tools.ietf.org/html/rfc5929
           - http://www.pyopenssl.org/en/stable/api/ssl.html#OpenSSL.SSL.Connection.get_finished
           - http://www.pyopenssl.org/en/stable/api/ssl.html#OpenSSL.SSL.Connection.get_peer_finished
        """
        return self._channel_id

    @channel_id.setter
    def channel_id(self, value: Dict[str, bytes]):
        self._channel_id = value

    @property
    def peer_cert(self) -> Dict[str, Any]:
        """
        If this transport is using TLS and the TLS peer has provided a valid certificate,
        this attribute returns the peer certificate.

        See `here <https://docs.python.org/3/library/ssl.html#ssl.SSLSocket.getpeercert>`_ for details
        about the object returned.
        """
        return self._peer_cert

    @peer_cert.setter
    def peer_cert(self, value: Dict[str, Any]):
        self._peer_cert = value

    @property
    def websocket_protocol(self) -> Optional[str]:
        """
        If the underlying connection uses a regular HTTP based WebSocket opening handshake,
        the WebSocket subprotocol negotiated, e.g. ``"wamp.2.cbor.batched"``.
        """
        return self._websocket_protocol

    @websocket_protocol.setter
    def websocket_protocol(self, value: Optional[str]):
        self._websocket_protocol = value

    @property
    def websocket_extensions_in_use(self) -> Optional[List[str]]:
        """
        If the underlying connection uses a regular HTTP based WebSocket opening handshake, the WebSocket extensions
        negotiated, e.g. ``["permessage-deflate", "client_no_context_takeover", "client_max_window_bits"]``.
        """
        return self._websocket_extensions_in_use

    @websocket_extensions_in_use.setter
    def websocket_extensions_in_use(self, value: Optional[List[str]]):
        self._websocket_extensions_in_use = value

    @property
    def http_headers_received(self) -> Dict[str, Any]:
        """
        If the underlying connection uses a regular HTTP based WebSocket opening handshake,
        the HTTP request headers as received from the client on this connection.
        """
        return self._http_headers_received

    @http_headers_received.setter
    def http_headers_received(self, value: Dict[str, Any]):
        self._http_headers_received = value

    @property
    def http_headers_sent(self) -> Dict[str, Any]:
        """
        If the underlying connection uses a regular HTTP based WebSocket opening handshake,
        the HTTP response headers as sent from the server on this connection.
        """
        return self._http_headers_sent

    @http_headers_sent.setter
    def http_headers_sent(self, value: Dict[str, Any]):
        self._http_headers_sent = value

    @property
    def http_cbtid(self) -> Optional[str]:
        """
        If the underlying connection uses a regular HTTP based WebSocket opening handshake,
        the HTTP cookie value of the WAMP tracking cookie if any is associated with this
        connection.
        """
        return self._http_cbtid

    @http_cbtid.setter
    def http_cbtid(self, value: Optional[str]):
        self._http_cbtid = value


@public
class SessionDetails(object):
    """
    Provides details for a WAMP session upon open.

    .. seealso:: :meth:`autobahn.wamp.interfaces.ISession.onJoin`
    """

    __slots__ = (
        "_realm",
        "_session",
        "_authid",
        "_authrole",
        "_authmethod",
        "_authprovider",
        "_authextra",
        "_serializer",
        "_transport",
        "_resumed",
        "_resumable",
        "_resume_token",
    )

    def __init__(
        self,
        realm: Optional[str] = None,
        session: Optional[int] = None,
        authid: Optional[str] = None,
        authrole: Optional[str] = None,
        authmethod: Optional[str] = None,
        authprovider: Optional[str] = None,
        authextra: Optional[Dict[str, Any]] = None,
        serializer: Optional[str] = None,
        transport: Optional[TransportDetails] = None,
        resumed: Optional[bool] = None,
        resumable: Optional[bool] = None,
        resume_token: Optional[str] = None,
    ):
        """

        :param realm: The WAMP realm this session is attached to, e.g. ``"realm1"``.
        :param session: WAMP session ID of this session, e.g. ``7069739155960584``.
        :param authid: The WAMP authid this session is joined as, e.g. ``"joe89"``
        :param authrole: The WAMP authrole this session is joined as, e.g. ``"user"``.
        :param authmethod: The WAMP authentication method the session is authenticated under,
            e.g. ``"anonymous"`` or ``"wampcra"``.
        :param authprovider: The WAMP authentication provider that handled the session authentication,
            e.g. ``"static"`` or ``"dynamic"``.
        :param authextra: The (optional) WAMP authentication extra that was provided to the authenticating session.
        :param serializer: The WAMP serializer (variant) this session is using,
            e.g. ``"json"`` or ``"cbor.batched"``.
        :param transport: The details of the WAMP transport this session is hosted on (communicates over).
        :param resumed: Whether the session is a resumed one.
        :param resumable: Whether this session can be resumed later.
        :param resume_token: The secure authorization token to resume the session.
        """
        self._realm = realm
        self._session = session
        self._authid = authid
        self._authrole = authrole
        self._authmethod = authmethod
        self._authprovider = authprovider
        self._authextra = authextra
        self._serializer = serializer
        self._transport = transport
        self._resumed = resumed
        self._resumable = resumable
        self._resume_token = resume_token

    def __eq__(self, other):
        """

        :param other:
        :return:
        """
        if not isinstance(other, self.__class__):
            return False
        if other._realm != self._realm:
            return False
        if other._session != self._session:
            return False
        if other._authid != self._authid:
            return False
        if other._authrole != self._authrole:
            return False
        if other._authmethod != self._authmethod:
            return False
        if other._authprovider != self._authprovider:
            return False
        if other._authextra != self._authextra:
            return False
        if other._serializer != self._serializer:
            return False
        if other._transport != self._transport:
            return False
        if other._resumed != self._resumed:
            return False
        if other._resumable != self._resumable:
            return False
        if other._resume_token != self._resume_token:
            return False
        return True

    def __ne__(self, other):
        """

        :param other:
        :return:
        """
        return not self.__eq__(other)

    @staticmethod
    def parse(data: Dict[str, Any]) -> "SessionDetails":
        """

        :param data:
        :return:
        """
        assert type(data) == dict

        obj = SessionDetails()

        if "realm" in data and data["realm"] is not None:
            if type(data["realm"]) != str:
                raise ValueError(
                    '"realm" must be a string, was {}'.format(type(data["realm"]))
                )
            obj._realm = data["realm"]

        if "session" in data and data["session"] is not None:
            if type(data["session"]) != int:
                raise ValueError(
                    '"session" must be an int, was {}'.format(type(data["session"]))
                )
            obj._session = data["session"]

        if "authid" in data and data["authid"] is not None:
            if type(data["authid"]) != str:
                raise ValueError(
                    '"authid" must be a string, was {}'.format(type(data["authid"]))
                )
            obj._authid = data["authid"]

        if "authrole" in data and data["authrole"] is not None:
            if type(data["authrole"]) != str:
                raise ValueError(
                    '"authrole" must be a string, was {}'.format(type(data["authrole"]))
                )
            obj._authrole = data["authrole"]

        if "authmethod" in data and data["authmethod"] is not None:
            if type(data["authmethod"]) != str:
                raise ValueError(
                    '"authmethod" must be a string, was {}'.format(
                        type(data["authmethod"])
                    )
                )
            obj._authmethod = data["authmethod"]

        if "authprovider" in data and data["authprovider"] is not None:
            if type(data["authprovider"]) != str:
                raise ValueError(
                    '"authprovider" must be a string, was {}'.format(
                        type(data["authprovider"])
                    )
                )
            obj._authprovider = data["authprovider"]

        if "authextra" in data and data["authextra"] is not None:
            if type(data["authextra"]) != dict:
                raise ValueError(
                    '"authextra" must be a dict, was {}'.format(type(data["authextra"]))
                )
            for key in data["authextra"].keys():
                if type(key) != str:
                    raise ValueError(
                        'key "{}" in authextra must be a string, was {}'.format(
                            key, type(key)
                        )
                    )
            obj._authextra = data["authextra"]

        if "serializer" in data and data["serializer"] is not None:
            if type(data["serializer"]) != str:
                raise ValueError(
                    '"serializer" must be a string, was {}'.format(
                        type(data["serializer"])
                    )
                )
            obj._serializer = data["serializer"]

        if "transport" in data and data["transport"] is not None:
            obj._transport = TransportDetails.parse(data["transport"])

        if "resumed" in data and data["resumed"] is not None:
            if type(data["resumed"]) != bool:
                raise ValueError(
                    '"resumed" must be a bool, was {}'.format(type(data["resumed"]))
                )
            obj._resumed = data["resumed"]

        if "resumable" in data and data["resumable"] is not None:
            if type(data["resumable"]) != bool:
                raise ValueError(
                    '"resumable" must be a bool, was {}'.format(type(data["resumable"]))
                )
            obj._resumable = data["resumable"]

        if "resume_token" in data and data["resume_token"] is not None:
            if type(data["resume_token"]) != str:
                raise ValueError(
                    '"resume_token" must be a string, was {}'.format(
                        type(data["resume_token"])
                    )
                )
            obj._resume_token = data["resume_token"]

        return obj

    def marshal(self) -> Dict[str, Any]:
        """

        :return:
        """
        obj = {
            "realm": self._realm,
            "session": self._session,
            "authid": self._authid,
            "authrole": self._authrole,
            "authmethod": self._authmethod,
            "authprovider": self._authprovider,
            "authextra": self._authextra,
            "serializer": self._serializer,
            "transport": self._transport.marshal() if self._transport else None,
            "resumed": self._resumed,
            "resumable": self._resumable,
            "resume_token": self._resume_token,
        }
        return obj

    def __str__(self) -> str:
        return pformat(self.marshal())

    @property
    def realm(self) -> Optional[str]:
        """
        The WAMP realm this session is attached to, e.g. ``"realm1"``.
        """
        return self._realm

    @realm.setter
    def realm(self, value: Optional[str]):
        self._realm = value

    @property
    def session(self) -> Optional[int]:
        """
        WAMP session ID of this session, e.g. ``7069739155960584``.
        """
        return self._session

    @session.setter
    def session(self, value: Optional[int]):
        self._session = value

    @property
    def authid(self) -> Optional[str]:
        """
        The WAMP authid this session is joined as, e.g. ``"joe89"``
        """
        return self._authid

    @authid.setter
    def authid(self, value: Optional[str]):
        self._authid = value

    @property
    def authrole(self) -> Optional[str]:
        """
        The WAMP authrole this session is joined as, e.g. ``"user"``.
        """
        return self._authrole

    @authrole.setter
    def authrole(self, value: Optional[str]):
        self._authrole = value

    @property
    def authmethod(self) -> Optional[str]:
        """
        The WAMP authentication method the session is authenticated under, e.g. ``"anonymous"``
        or ``"wampcra"``.
        """
        return self._authmethod

    @authmethod.setter
    def authmethod(self, value: Optional[str]):
        self._authmethod = value

    @property
    def authprovider(self) -> Optional[str]:
        """
        The WAMP authentication provider that handled the session authentication, e.g. ``"static"``
        or ``"dynamic"``.
        """
        return self._authprovider

    @authprovider.setter
    def authprovider(self, value: Optional[str]):
        self._authprovider = value

    @property
    def authextra(self) -> Optional[Dict[str, Any]]:
        """
        The (optional) WAMP authentication extra that was provided to the authenticating session.
        """
        return self._authextra

    @authextra.setter
    def authextra(self, value: Optional[Dict[str, Any]]):
        self._authextra = value

    @property
    def serializer(self) -> Optional[str]:
        """
        The WAMP serializer (variant) this session is using, e.g. ``"json"`` or ``"cbor.batched"``.
        """
        return self._serializer

    @serializer.setter
    def serializer(self, value: Optional[str]):
        self._serializer = value

    @property
    def transport(self) -> Optional[TransportDetails]:
        """
        The details of the WAMP transport this session is hosted on (communicates over).
        """
        return self._transport

    @transport.setter
    def transport(self, value: Optional[TransportDetails]):
        self._transport = value

    @property
    def resumed(self) -> Optional[bool]:
        """
        Whether the session is a resumed one.
        """
        return self._resumed

    @resumed.setter
    def resumed(self, value: Optional[bool]):
        self._resumed = value

    @property
    def resumable(self) -> Optional[bool]:
        """
        Whether this session can be resumed later.
        """
        return self._resumable

    @resumable.setter
    def resumable(self, value: Optional[bool]):
        self._resumable = value

    @property
    def resume_token(self) -> Optional[str]:
        """
        The secure authorization token to resume the session.
        """
        return self._resume_token

    @resume_token.setter
    def resume_token(self, value: Optional[str]):
        self._resume_token = value
