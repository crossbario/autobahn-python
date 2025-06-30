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


from autobahn.util import public
from autobahn.wamp.uri import error

__all__ = (
    "ApplicationError",
    "Error",
    "InvalidPayload",
    "InvalidUri",
    "InvalidUriError",
    "NotAuthorized",
    "ProtocolError",
    "SerializationError",
    "SessionNotReady",
    "TransportLost",
    "TypeCheckError",
)


@public
class Error(RuntimeError):
    """
    Base class for all exceptions related to WAMP.
    """


@public
class SessionNotReady(Error):
    """
    The application tried to perform a WAMP interaction, but the
    session is not yet fully established.
    """


@public
class SerializationError(Error):
    """
    Exception raised when the WAMP serializer could not serialize the
    application payload (``args`` or ``kwargs`` for ``CALL``, ``PUBLISH``, etc).
    """


@public
class InvalidUriError(Error):
    """
    Exception raised when an invalid WAMP URI was used.
    """


@public
class ProtocolError(Error):
    """
    Exception raised when WAMP protocol was violated. Protocol errors
    are fatal and are handled by the WAMP implementation. They are
    not supposed to be handled at the application level.
    """


@public
class TransportLost(Error):
    """
    Exception raised when the transport underlying the WAMP session
    was lost or is not connected.
    """


@public
class ApplicationError(Error):
    """
    Base class for all exceptions that can/may be handled
    at the application level.
    """

    INVALID_URI = "wamp.error.invalid_uri"
    """
    Peer provided an incorrect URI for a URI-based attribute of a WAMP message
    such as a realm, topic or procedure.
    """

    INVALID_PAYLOAD = "wamp.error.invalid_payload"
    """
    The application payload could not be serialized.
    """

    PAYLOAD_SIZE_EXCEEDED = "wamp.error.payload_size_exceeded"
    """
    The application payload could not be transported becuase the serialized/framed payload
    exceeds the transport limits.
    """

    NO_SUCH_PROCEDURE = "wamp.error.no_such_procedure"
    """
    A Dealer could not perform a call, since not procedure is currently registered
    under the given URI.
    """

    PROCEDURE_ALREADY_EXISTS = "wamp.error.procedure_already_exists"
    """
    A procedure could not be registered, since a procedure with the given URI is
    already registered.
    """

    PROCEDURE_EXISTS_INVOCATION_POLICY_CONFLICT = (
        "wamp.error.procedure_exists_with_different_invocation_policy"
    )
    """
    A procedure could not be registered, since a procedure with the given URI is
    already registered, and the registration has a conflicting invocation policy.
    """

    NO_SUCH_REGISTRATION = "wamp.error.no_such_registration"
    """
    A Dealer could not perform a unregister, since the given registration is not active.
    """

    NO_SUCH_SUBSCRIPTION = "wamp.error.no_such_subscription"
    """
    A Broker could not perform a unsubscribe, since the given subscription is not active.
    """

    NO_SUCH_SESSION = "wamp.error.no_such_session"
    """
    A router could not perform an operation, since a session ID specified was non-existant.
    """

    INVALID_ARGUMENT = "wamp.error.invalid_argument"
    """
    A call failed, since the given argument types or values are not acceptable to the
    called procedure - in which case the *Callee* may throw this error. Or a Router
    performing *payload validation* checked the payload (``args`` / ``kwargs``) of a call,
    call result, call error or publish, and the payload did not conform.
    """

    # FIXME: this currently isn't used neither in Autobahn nor Crossbar. Check!
    SYSTEM_SHUTDOWN = "wamp.error.system_shutdown"
    """
    The *Peer* is shutting down completely - used as a ``GOODBYE`` (or ``ABORT``) reason.
    """

    # FIXME: this currently isn't used neither in Autobahn nor Crossbar. Check!
    CLOSE_REALM = "wamp.error.close_realm"
    """
    The *Peer* want to leave the realm - used as a ``GOODBYE`` reason.
    """

    # FIXME: this currently isn't used neither in Autobahn nor Crossbar. Check!
    GOODBYE_AND_OUT = "wamp.error.goodbye_and_out"
    """
    A *Peer* acknowledges ending of a session - used as a ``GOOBYE`` reply reason.
    """

    NOT_AUTHORIZED = "wamp.error.not_authorized"
    """
    A call, register, publish or subscribe failed, since the session is not authorized
    to perform the operation.
    """

    AUTHORIZATION_FAILED = "wamp.error.authorization_failed"
    """
    A Dealer or Broker could not determine if the *Peer* is authorized to perform
    a join, call, register, publish or subscribe, since the authorization operation
    *itself* failed. E.g. a custom authorizer did run into an error.
    """

    AUTHENTICATION_FAILED = "wamp.error.authentication_failed"
    """
    Something failed with the authentication itself, that is, authentication could
    not run to end.
    """

    NO_AUTH_METHOD = "wamp.error.no_auth_method"
    """
    No authentication method the peer offered is available or active.
    """

    NO_SUCH_REALM = "wamp.error.no_such_realm"
    """
    Peer wanted to join a non-existing realm (and the *Router* did not allow to auto-create
    the realm).
    """

    NO_SUCH_ROLE = "wamp.error.no_such_role"
    """
    A *Peer* was to be authenticated under a Role that does not (or no longer) exists on the Router.
    For example, the *Peer* was successfully authenticated, but the Role configured does not
    exists - hence there is some misconfiguration in the Router.
    """

    NO_SUCH_PRINCIPAL = "wamp.error.no_such_principal"
    """
    A *Peer* was authenticated for an authid that does not or longer exists.
    """

    CANCELED = "wamp.error.canceled"
    """
    A Dealer or Callee canceled a call previously issued (WAMP AP).
    """

    TIMEOUT = "wamp.error.timeout"
    """
    A pending (in-flight) call was timed out.
    """

    # FIXME: this currently isn't used neither in Autobahn nor Crossbar. Check!
    NO_ELIGIBLE_CALLEE = "wamp.error.no_eligible_callee"
    """
    A *Dealer* could not perform a call, since a procedure with the given URI is registered,
    but *Callee Black- and Whitelisting* and/or *Caller Exclusion* lead to the
    exclusion of (any) *Callee* providing the procedure (WAMP AP).
    """

    ENC_NO_PAYLOAD_CODEC = "wamp.error.no_payload_codec"
    """
    WAMP message in payload transparency mode received, but no codec set
    or codec did not decode the payload.
    """

    ENC_TRUSTED_URI_MISMATCH = "wamp.error.encryption.trusted_uri_mismatch"
    """
    WAMP-cryptobox application payload end-to-end encryption error.
    """

    ENC_DECRYPT_ERROR = "wamp.error.encryption.decrypt_error"
    """
    WAMP-cryptobox application payload end-to-end encryption error.
    """

    TYPE_CHECK_ERROR = "wamp.error.type_check_error"
    """
    WAMP procedure called with wrong argument types or subscription published
    with wrong argument types.
    """

    def __init__(self, error, *args, **kwargs):
        """

        :param error: The URI of the error that occurred, e.g. ``wamp.error.not_authorized``.
        :type error: str
        """
        Exception.__init__(self, *args)
        self.kwargs = kwargs
        self.error = error
        self.enc_algo = kwargs.pop("enc_algo", None)
        self.callee = kwargs.pop("callee", None)
        self.callee_authid = kwargs.pop("callee_authid", None)
        self.callee_authrole = kwargs.pop("callee_authrole", None)
        self.forward_for = kwargs.pop("forward_for", None)

    @public
    def error_message(self):
        """
        Get the error message of this exception.

        :returns: The error message.
        :rtype: str
        """
        return "{0}: {1}".format(
            self.error,
            " ".join([str(a) for a in self.args]),
        )

    def __unicode__(self):
        if self.kwargs and "traceback" in self.kwargs:
            tb = ":\n" + self.kwargs.pop("traceback") + "\n"
            self.kwargs["traceback"] = "..."
        else:
            tb = ""
        return "ApplicationError(error=<{0}>, args={1}, kwargs={2}, enc_algo={3}, callee={4}, callee_authid={5}, callee_authrole={6}, forward_for={7}){8}".format(
            self.error,
            list(self.args),
            self.kwargs,
            self.enc_algo,
            self.callee,
            self.callee_authid,
            self.callee_authrole,
            self.forward_for,
            tb,
        )

    def __str__(self):
        return self.__unicode__()


@error(ApplicationError.NOT_AUTHORIZED)
class NotAuthorized(Exception):
    """
    Not authorized to perform the respective action.
    """


@error(ApplicationError.INVALID_URI)
class InvalidUri(Exception):
    """
    The URI for a topic, procedure or error is not a valid WAMP URI.
    """


@error(ApplicationError.INVALID_PAYLOAD)
class InvalidPayload(Exception):
    """
    The URI for a topic, procedure or error is not a valid WAMP URI.
    """


class TypeCheckError(ApplicationError):
    """
    The URI for a topic published with invalid argument types or a
    procedure called with invalid arguments types.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(ApplicationError.TYPE_CHECK_ERROR, *args, **kwargs)
