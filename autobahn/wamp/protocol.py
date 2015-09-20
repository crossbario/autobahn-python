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
import txaio
import inspect

from autobahn import wamp
from autobahn.wamp import uri
from autobahn.wamp import message
from autobahn.wamp import types
from autobahn.wamp import role
from autobahn.wamp import exception
from autobahn.wamp.exception import ApplicationError, ProtocolError, SessionNotReady, SerializationError
from autobahn.wamp.interfaces import IApplicationSession, ISession  # noqa
from autobahn.wamp.types import SessionDetails
from autobahn.util import IdGenerator

from autobahn.wamp.request import \
    Publication, \
    Subscription, \
    Handler, \
    Registration, \
    Endpoint, \
    PublishRequest, \
    SubscribeRequest, \
    UnsubscribeRequest, \
    CallRequest, \
    InvocationRequest, \
    RegisterRequest, \
    UnregisterRequest


def is_method_or_function(f):
    return inspect.ismethod(f) or inspect.isfunction(f)


class BaseSession(object):
    """
    WAMP session base class.

    This class implements :class:`autobahn.wamp.interfaces.ISession`.
    """

    def __init__(self):
        """

        """
        # this is for library level debugging
        self.debug = False

        # this is for app level debugging. exceptions raised in user code
        # will get logged (that is, when invoking remoted procedures or
        # when invoking event handlers)
        self.debug_app = False

        # this is for marshalling traceback from exceptions thrown in user
        # code within WAMP error messages (that is, when invoking remoted
        # procedures)
        self.traceback_app = False

        # mapping of exception classes to WAMP error URIs
        self._ecls_to_uri_pat = {}

        # mapping of WAMP error URIs to exception classes
        self._uri_to_ecls = {
            ApplicationError.INVALID_PAYLOAD: SerializationError
        }

        # session authentication information
        self._authid = None
        self._authrole = None
        self._authmethod = None
        self._authprovider = None

        # generator for WAMP request IDs
        self._request_id_gen = IdGenerator()

    def define(self, exception, error=None):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.define`
        """
        if error is None:
            assert(hasattr(exception, '_wampuris'))
            self._ecls_to_uri_pat[exception] = exception._wampuris
            self._uri_to_ecls[exception._wampuris[0].uri()] = exception
        else:
            assert(not hasattr(exception, '_wampuris'))
            self._ecls_to_uri_pat[exception] = [uri.Pattern(six.u(error), uri.Pattern.URI_TARGET_HANDLER)]
            self._uri_to_ecls[six.u(error)] = exception

    def _message_from_exception(self, request_type, request, exc, tb=None):
        """
        Create a WAMP error message from an exception.

        :param request_type: The request type this WAMP error message is for.
        :type request_type: int
        :param request: The request ID this WAMP error message is for.
        :type request: int
        :param exc: The exception.
        :type exc: Instance of :class:`Exception` or subclass thereof.
        :param tb: Optional traceback. If present, it'll be included with the WAMP error message.
        :type tb: list or None
        """
        args = None
        if hasattr(exc, 'args'):
            args = list(exc.args)  # make sure tuples are made into lists

        kwargs = None
        if hasattr(exc, 'kwargs'):
            kwargs = exc.kwargs

        if tb:
            if kwargs:
                kwargs['traceback'] = tb
            else:
                kwargs = {'traceback': tb}

        if isinstance(exc, exception.ApplicationError):
            error = exc.error if type(exc.error) == six.text_type else six.u(exc.error)
        else:
            if exc.__class__ in self._ecls_to_uri_pat:
                error = self._ecls_to_uri_pat[exc.__class__][0]._uri
            else:
                error = u"wamp.error.runtime_error"

        msg = message.Error(request_type, request, error, args, kwargs)

        return msg

    def _exception_from_message(self, msg):
        """
        Create a user (or generic) exception from a WAMP error message.

        :param msg: A WAMP error message.
        :type msg: instance of :class:`autobahn.wamp.message.Error`
        """

        # FIXME:
        # 1. map to ecls based on error URI wildcard/prefix
        # 2. extract additional args/kwargs from error URI

        exc = None

        if msg.error in self._uri_to_ecls:
            ecls = self._uri_to_ecls[msg.error]
            try:
                # the following might fail, eg. TypeError when
                # signature of exception constructor is incompatible
                # with args/kwargs or when the exception constructor raises
                if msg.kwargs:
                    if msg.args:
                        exc = ecls(*msg.args, **msg.kwargs)
                    else:
                        exc = ecls(**msg.kwargs)
                else:
                    if msg.args:
                        exc = ecls(*msg.args)
                    else:
                        exc = ecls()
            except Exception:
                try:
                    self.onUserError(
                        txaio.create_failure(),
                        "While re-constructing exception",
                    )
                except:
                    pass

        if not exc:
            # the following ctor never fails ..
            if msg.kwargs:
                if msg.args:
                    exc = exception.ApplicationError(msg.error, *msg.args, **msg.kwargs)
                else:
                    exc = exception.ApplicationError(msg.error, **msg.kwargs)
            else:
                if msg.args:
                    exc = exception.ApplicationError(msg.error, *msg.args)
                else:
                    exc = exception.ApplicationError(msg.error)

        return exc


ISession.register(BaseSession)


class _Listener(object):
    """
    Internal helper.

    A class which is instantiated to provide listener functionality
    like:

        # js-like
        connection.on('open', callback)
        # attribute-access style:
        connection.on.open(callback)
        # add/remove style:
        connection.on.open.add(callback)
        # they all need something like this for removal:
        connection.on.open.remove(callback)

    XXX I guess should probably decide on ONE way, but this
    abstraction is nice to avoid copy-pasting code to track lists of
    callbacks and invoke them wherever we need listeners...
    """

    log = txaio.make_logger()

    def __init__(self):
        self._listeners = set()

    def add(self, callback):
        """
        Add a callback to this listener
        """
        self._listeners.add(callback)

    __call__ = add  #: alias for "add"

    def remove(self, callback):
        """
        Remove a callback from this listener
        """
        self._listeners.remove(callback)

    def _notify(self, *args, **kw):
        """
        Calls all listeners with the specified args.

        Returns a Deferred which callbacks when all the listeners
        which return Deferreds/Futures have themselves completed.
        """
        calls = []

        def failed(fail):
            self.log.error("Notifying listener failed: {msg}", msg=txaio.failure_message(fail))
            self.log.debug("{traceback}", traceback=txaio.failure_format_traceback(fail))

        for cb in self._listeners:
            f = txaio.as_future(cb, *args, **kw)
            txaio.add_callbacks(f, None, failed)
            calls.append(f)
        return txaio.gather(calls)


class _ListenerCollection(object):
    """
    Internal helper.

    This collects all your valid event listeners together in one
    object if you want.
    """
    def __init__(self, valid_events):
        self._valid_events = valid_events
        for e in valid_events:
            setattr(self, e, _Listener())

    def __call__(self, event, callback):
        if event not in self._valid_events:
            raise Exception("Invalid event '{}'".format(event))
        getattr(self, event).add(callback)

    def remove(self, event, callback):
        if event not in self._valid_events:
            raise Exception("Invalid event '{}'".format(event))
        getattr(self, event).remove(callback)


class ApplicationSession(BaseSession):
    """
    WAMP endpoint session. This class implements

    * :class:`autobahn.wamp.interfaces.IPublisher`
    * :class:`autobahn.wamp.interfaces.ISubscriber`
    * :class:`autobahn.wamp.interfaces.ICaller`
    * :class:`autobahn.wamp.interfaces.ICallee`
    * :class:`autobahn.wamp.interfaces.ITransportHandler`

    It also emits several events, corresponding to some of the methods
    you can override. You can choose to use either interface (even
    mixing and matching). Any callback can by asynchronous
    (i.e. return a Future/Deferred).

    The events are:

      * `"join"`: the session has been established, and `onJoin` has run

    You may add event listeners as so::

        def joined(session):
            print("A session is now joined:", session)
        session.on('join', joined)  # "session" is an ApplicationSession instance
        session.on.join(joined)  # "session" is an ApplicationSession instance

    All the callbacks take a single argument (the session instance)
    except disconnect, which receives either `closed` or `lost`
    """

    log = txaio.make_logger()

    def __init__(self, config=None):
        """
        Constructor.
        """
        BaseSession.__init__(self)
        self.config = config or types.ComponentConfig(realm=u"default")

        # events which can be listened for
        # XXX so can do:
        #    session.on.join(callback)
        #    session.on.leave(callback)
        #    session.on.join.remove(callback)
        # or:
        #    session.on.join.add(callback)
        # or:
        #    session.on('join', callback)
        #    session.on.remove('join', callback)
        self.on = _ListenerCollection(['join', 'leave', 'ready', 'connect', 'disconnect'])

        self._transport = None
        self._session_id = None
        self._realm = None

        self._goodbye_sent = False
        self._transport_is_closing = False

        # outstanding requests
        self._publish_reqs = {}
        self._subscribe_reqs = {}
        self._unsubscribe_reqs = {}
        self._call_reqs = {}
        self._register_reqs = {}
        self._unregister_reqs = {}

        # subscriptions in place
        self._subscriptions = {}

        # registrations in place
        self._registrations = {}

        # incoming invocations
        self._invocations = {}

    def onOpen(self, transport):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onOpen`
        """
        self._transport = transport
        d = txaio.as_future(self.onConnect)

        def do_connect(rtn):
            d1 = self.on.connect._notify(self)
            txaio.add_callbacks(d1, lambda _: rtn, None)
        txaio.add_callbacks(d, do_connect, None)

        def _error(e):
            return self._swallow_error(e, "While firing onConnect")
        txaio.add_callbacks(d, None, _error)

    def onConnect(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.onConnect`
        """
        self.join(self.config.realm)

    def join(self, realm, authmethods=None, authid=None):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.join`
        """
        if six.PY2 and type(realm) == str:
            realm = six.u(realm)
        if six.PY2 and type(authid) == str:
            authid = six.u(authid)

        if self._session_id:
            raise Exception("already joined")

        self._goodbye_sent = False

        msg = message.Hello(realm, role.DEFAULT_CLIENT_ROLES, authmethods, authid)
        self._realm = realm
        self._transport.send(msg)

    def disconnect(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.disconnect`
        """
        if self._transport:
            self._transport.close()

    def is_connected(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.is_connected`
        """
        return self._transport is not None

    def onUserError(self, fail, msg):
        """
        This is called when we try to fire a callback, but get an
        exception from user code -- for example, a registered publish
        callback or a registered method. By default, this prints the
        current stack-trace and then error-message to stdout.

        ApplicationSession-derived objects may override this to
        provide logging if they prefer. The Twisted implemention does
        this. (See :class:`autobahn.twisted.wamp.ApplicationSession`)

        :param fail: instance implementing txaio.IFailedFuture

        :param msg: an informative message from the library. It is
            suggested you log this immediately after the exception.
        """
        if isinstance(fail.value, exception.ApplicationError):
            self.log.error(fail.value.error_message())
        else:
            self.log.error(
                '{msg}',
                msg=txaio.failure_format_traceback(fail),
            )
            self.log.debug(
                '{msg}: {traceback}',
                msg=msg,
                traceback=txaio.failure_format_traceback(fail),
            )

    def _swallow_error(self, fail, msg):
        '''
        This is an internal generic error-handler for errors encountered
        when calling down to on*() handlers that can reasonably be
        expected to be overridden in user code.

        Note that it *cancels* the error, so use with care!

        Specifically, this should *never* be added to the errback
        chain for a Deferred/coroutine that will make it out to user
        code.
        '''
        try:
            self.onUserError(fail, msg)
        except:
            pass
        return None

    def onMessage(self, msg):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onMessage`
        """
        if self._session_id is None:

            # the first message must be WELCOME, ABORT or CHALLENGE ..
            if isinstance(msg, message.Welcome):
                self._session_id = msg.session

                details = SessionDetails(self._realm, self._session_id, msg.authid, msg.authrole, msg.authmethod)

                d = self.on.join._notify(self, details)
                txaio.add_callbacks(d, lambda _: txaio.as_future(self.onJoin, details), None)
                txaio.add_callbacks(d, lambda _: self.on.ready._notify(self), None)

                def _error(e):
                    return self._swallow_error(e, "While firing onJoin")
                txaio.add_callbacks(d, None, _error)

            elif isinstance(msg, message.Abort):

                # fire callback
                # note: we do not close the transport here as the WAMP
                # session joining/leaving is independant from the
                # transport
                details = types.CloseDetails(msg.reason, msg.message)

                d = self.on.leave._notify(self, details)
                txaio.add_callbacks(d, lambda _: txaio.as_future(self.onLeave, details), None)

                def _error(e):
                    return self._swallow_error(e, "While firing onLeave")
                txaio.add_callbacks(d, None, _error)

            elif isinstance(msg, message.Challenge):

                challenge = types.Challenge(msg.method, msg.extra)
                d = txaio.as_future(self.onChallenge, challenge)

                def success(signature):
                    reply = message.Authenticate(signature)
                    self._transport.send(reply)

                def error(err):
                    reply = message.Abort(u"wamp.error.cannot_authenticate", u"{0}".format(err.value))
                    self._transport.send(reply)
                    # fire callback and close the transport
                    details = types.CloseDetails(reply.reason, reply.message)
                    d = self.on.leave._notify(self, details)
                    txaio.add_callbacks(d, lambda _: txaio.as_future(self.onLeave, details), None)

                    def _error(e):
                        return self._swallow_error(e, "While firing onLeave")
                    txaio.add_callbacks(d, None, _error)
                    # switching to the callback chain, effectively
                    # cancelling error (which we've now handled)
                    return d

                txaio.add_callbacks(d, success, error)

            else:
                raise ProtocolError("Received {0} message, and session is not yet established".format(msg.__class__))

        else:
            # self._session_id != None (aka "session established")
            if isinstance(msg, message.Goodbye):
                if not self._goodbye_sent:
                    # the peer wants to close: send GOODBYE reply
                    reply = message.Goodbye()
                    self._transport.send(reply)

                self._session_id = None

                # fire callback and close the transport
                details = types.CloseDetails(msg.reason, msg.message)
                d = self.on.leave._notify(self, details)
                txaio.add_callbacks(d, lambda _: txaio.as_future(self.onLeave, details), None)

                def _error(e):
                    errmsg = 'While firing onLeave for reason "{0}" and message "{1}"'.format(msg.reason, msg.message)
                    return self._swallow_error(e, errmsg)
                txaio.add_callbacks(d, None, _error)

            elif isinstance(msg, message.Event):

                if msg.subscription in self._subscriptions:

                    # fire all event handlers on subscription ..
                    for subscription in self._subscriptions[msg.subscription]:

                        handler = subscription.handler

                        invoke_args = (handler.obj,) if handler.obj else tuple()
                        if msg.args:
                            invoke_args = invoke_args + tuple(msg.args)

                        invoke_kwargs = msg.kwargs if msg.kwargs else dict()
                        if handler.details_arg:
                            invoke_kwargs[handler.details_arg] = types.EventDetails(publication=msg.publication, publisher=msg.publisher, topic=msg.topic)

                        def _error(e):
                            errmsg = 'While firing {0} subscribed under {1}.'.format(
                                handler.fn, msg.subscription)
                            return self._swallow_error(e, errmsg)

                        future = txaio.as_future(handler.fn, *invoke_args, **invoke_kwargs)
                        txaio.add_callbacks(future, None, _error)

                else:
                    raise ProtocolError("EVENT received for non-subscribed subscription ID {0}".format(msg.subscription))

            elif isinstance(msg, message.Published):

                if msg.request in self._publish_reqs:

                    # get and pop outstanding publish request
                    publish_request = self._publish_reqs.pop(msg.request)

                    # create a new publication object
                    publication = Publication(msg.publication)

                    # resolve deferred/future for publishing successfully
                    txaio.resolve(publish_request.on_reply, publication)
                else:
                    raise ProtocolError("PUBLISHED received for non-pending request ID {0}".format(msg.request))

            elif isinstance(msg, message.Subscribed):

                if msg.request in self._subscribe_reqs:

                    # get and pop outstanding subscribe request
                    request = self._subscribe_reqs.pop(msg.request)

                    # create new handler subscription list for subscription ID if not yet tracked
                    if msg.subscription not in self._subscriptions:
                        self._subscriptions[msg.subscription] = []

                    subscription = Subscription(msg.subscription, self, request.handler)

                    # add handler to existing subscription
                    self._subscriptions[msg.subscription].append(subscription)

                    # resolve deferred/future for subscribing successfully
                    txaio.resolve(request.on_reply, subscription)
                else:
                    raise ProtocolError("SUBSCRIBED received for non-pending request ID {0}".format(msg.request))

            elif isinstance(msg, message.Unsubscribed):

                if msg.request in self._unsubscribe_reqs:

                    # get and pop outstanding subscribe request
                    request = self._unsubscribe_reqs.pop(msg.request)

                    # if the subscription still exists, mark as inactive and remove ..
                    if request.subscription_id in self._subscriptions:
                        for subscription in self._subscriptions[request.subscription_id]:
                            subscription.active = False
                        del self._subscriptions[request.subscription_id]

                    # resolve deferred/future for unsubscribing successfully
                    txaio.resolve(request.on_reply, 0)
                else:
                    raise ProtocolError("UNSUBSCRIBED received for non-pending request ID {0}".format(msg.request))

            elif isinstance(msg, message.Result):

                if msg.request in self._call_reqs:

                    if msg.progress:

                        # progressive result
                        call_request = self._call_reqs[msg.request]
                        if call_request.options.on_progress:
                            kw = msg.kwargs or dict()
                            args = msg.args or tuple()
                            try:
                                # XXX what if on_progress returns a Deferred/Future?
                                call_request.options.on_progress(*args, **kw)
                            except Exception:
                                try:
                                    self.onUserError(
                                        txaio.create_failure(),
                                        "While firing on_progress",
                                    )
                                except:
                                    pass

                        else:
                            # silently ignore progressive results
                            pass

                    else:
                        # final result
                        #
                        call_request = self._call_reqs.pop(msg.request)

                        on_reply = call_request.on_reply

                        if msg.kwargs:
                            if msg.args:
                                res = types.CallResult(*msg.args, **msg.kwargs)
                            else:
                                res = types.CallResult(**msg.kwargs)
                            txaio.resolve(on_reply, res)
                        else:
                            if msg.args:
                                if len(msg.args) > 1:
                                    res = types.CallResult(*msg.args)
                                    txaio.resolve(on_reply, res)
                                else:
                                    txaio.resolve(on_reply, msg.args[0])
                            else:
                                txaio.resolve(on_reply, None)
                else:
                    raise ProtocolError("RESULT received for non-pending request ID {0}".format(msg.request))

            elif isinstance(msg, message.Invocation):

                if msg.request in self._invocations:

                    raise ProtocolError("INVOCATION received for request ID {0} already invoked".format(msg.request))

                else:

                    if msg.registration not in self._registrations:

                        raise ProtocolError("INVOCATION received for non-registered registration ID {0}".format(msg.registration))

                    else:
                        registration = self._registrations[msg.registration]
                        endpoint = registration.endpoint

                        if endpoint.obj is not None:
                            invoke_args = (endpoint.obj,)
                        else:
                            invoke_args = tuple()

                        if msg.args:
                            invoke_args = invoke_args + tuple(msg.args)

                        invoke_kwargs = msg.kwargs if msg.kwargs else dict()

                        if endpoint.details_arg:

                            if msg.receive_progress:
                                def progress(*args, **kwargs):
                                    progress_msg = message.Yield(msg.request, args=args, kwargs=kwargs, progress=True)
                                    self._transport.send(progress_msg)
                            else:
                                progress = None

                            invoke_kwargs[endpoint.details_arg] = types.CallDetails(progress, caller=msg.caller, procedure=msg.procedure)

                        on_reply = txaio.as_future(endpoint.fn, *invoke_args, **invoke_kwargs)

                        def success(res):
                            del self._invocations[msg.request]

                            if isinstance(res, types.CallResult):
                                reply = message.Yield(msg.request, args=res.results, kwargs=res.kwresults)
                            else:
                                reply = message.Yield(msg.request, args=[res])

                            try:
                                self._transport.send(reply)
                            except SerializationError as e:
                                # the application-level payload returned from the invoked procedure can't be serialized
                                reply = message.Error(message.Invocation.MESSAGE_TYPE, msg.request, ApplicationError.INVALID_PAYLOAD,
                                                      args=[u'success return value from invoked procedure "{0}" could not be serialized: {1}'.format(registration.procedure, e)])
                                self._transport.send(reply)

                        def error(err):
                            # errmsg = 'Failure while invoking procedure {0} registered under "{1}: {2}".'.format(endpoint.fn, registration.procedure, err)
                            errmsg = "{0}".format(err.value.args[0])
                            try:
                                self.onUserError(err, errmsg)
                            except:
                                pass
                            formatted_tb = None
                            if self.traceback_app:
                                formatted_tb = txaio.failure_format_traceback(err)

                            del self._invocations[msg.request]

                            if hasattr(err, 'value'):
                                exc = err.value
                            else:
                                exc = err

                            reply = self._message_from_exception(message.Invocation.MESSAGE_TYPE, msg.request, exc, formatted_tb)

                            try:
                                self._transport.send(reply)
                            except SerializationError as e:
                                # the application-level payload returned from the invoked procedure can't be serialized
                                reply = message.Error(message.Invocation.MESSAGE_TYPE, msg.request, ApplicationError.INVALID_PAYLOAD,
                                                      args=[u'error return value from invoked procedure "{0}" could not be serialized: {1}'.format(registration.procedure, e)])
                                self._transport.send(reply)
                            # we have handled the error, so we eat it
                            return None

                        self._invocations[msg.request] = InvocationRequest(msg.request, on_reply)

                        txaio.add_callbacks(on_reply, success, error)

            elif isinstance(msg, message.Interrupt):

                if msg.request not in self._invocations:
                    raise ProtocolError("INTERRUPT received for non-pending invocation {0}".format(msg.request))
                else:
                    # noinspection PyBroadException
                    try:
                        self._invocations[msg.request].cancel()
                    except Exception:
                        # XXX can .cancel() return a Deferred/Future?
                        try:
                            self.onUserError(
                                txaio.create_failure(),
                                "While cancelling call.",
                            )
                        except:
                            pass
                    finally:
                        del self._invocations[msg.request]

            elif isinstance(msg, message.Registered):

                if msg.request in self._register_reqs:

                    # get and pop outstanding register request
                    request = self._register_reqs.pop(msg.request)

                    # create new registration if not yet tracked
                    if msg.registration not in self._registrations:
                        registration = Registration(self, msg.registration, request.procedure, request.endpoint)
                        self._registrations[msg.registration] = registration
                    else:
                        raise ProtocolError("REGISTERED received for already existing registration ID {0}".format(msg.registration))

                    txaio.resolve(request.on_reply, registration)
                else:
                    raise ProtocolError("REGISTERED received for non-pending request ID {0}".format(msg.request))

            elif isinstance(msg, message.Unregistered):

                if msg.request in self._unregister_reqs:

                    # get and pop outstanding subscribe request
                    request = self._unregister_reqs.pop(msg.request)

                    # if the registration still exists, mark as inactive and remove ..
                    if request.registration_id in self._registrations:
                        self._registrations[request.registration_id].active = False
                        del self._registrations[request.registration_id]

                    # resolve deferred/future for unregistering successfully
                    txaio.resolve(request.on_reply)
                else:
                    raise ProtocolError("UNREGISTERED received for non-pending request ID {0}".format(msg.request))

            elif isinstance(msg, message.Error):

                # remove outstanding request and get the reply deferred/future
                on_reply = None

                # ERROR reply to CALL
                if msg.request_type == message.Call.MESSAGE_TYPE and msg.request in self._call_reqs:
                    on_reply = self._call_reqs.pop(msg.request).on_reply

                # ERROR reply to PUBLISH
                elif msg.request_type == message.Publish.MESSAGE_TYPE and msg.request in self._publish_reqs:
                    on_reply = self._publish_reqs.pop(msg.request).on_reply

                # ERROR reply to SUBSCRIBE
                elif msg.request_type == message.Subscribe.MESSAGE_TYPE and msg.request in self._subscribe_reqs:
                    on_reply = self._subscribe_reqs.pop(msg.request).on_reply

                # ERROR reply to UNSUBSCRIBE
                elif msg.request_type == message.Unsubscribe.MESSAGE_TYPE and msg.request in self._unsubscribe_reqs:
                    on_reply = self._unsubscribe_reqs.pop(msg.request).on_reply

                # ERROR reply to REGISTER
                elif msg.request_type == message.Register.MESSAGE_TYPE and msg.request in self._register_reqs:
                    on_reply = self._register_reqs.pop(msg.request).on_reply

                # ERROR reply to UNREGISTER
                elif msg.request_type == message.Unregister.MESSAGE_TYPE and msg.request in self._unregister_reqs:
                    on_reply = self._unregister_reqs.pop(msg.request).on_reply

                if on_reply:
                    txaio.reject(on_reply, self._exception_from_message(msg))
                else:
                    raise ProtocolError("WampAppSession.onMessage(): ERROR received for non-pending request_type {0} and request ID {1}".format(msg.request_type, msg.request))

            else:

                raise ProtocolError("Unexpected message {0}".format(msg.__class__))

    # noinspection PyUnusedLocal
    def onClose(self, wasClean):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onClose`
        """
        self._transport = None
        if self._session_id:
            # fire callback and close the transport
            details = types.CloseDetails(reason=types.CloseDetails.REASON_TRANSPORT_LOST,
                                         message="WAMP transport was lost without closing the session before")
            d = self.on.leave._notify(self, details)
            txaio.add_callbacks(d, lambda _: txaio.as_future(self.onLeave, details), None)

            def _error(e):
                return self._swallow_error(e, "While firing onLeave")
            txaio.add_callbacks(d, None, _error)

            self._session_id = None

# XXX hmm, why do "all" the tests fail if I try chaining to d?
#        else:
#            d = txaio.create_future_success(None)

        # XXX do we want to chain these to "d" from if block above? (yes) (hmm: maybe not
        d2 = txaio.as_future(self.onDisconnect)

        def notify_disconnect(rtn):
            detail = 'closed' if wasClean else 'lost'
            d1 = self.on.disconnect._notify(self, detail)
            txaio.add_callbacks(d1, lambda _: rtn, None)
            return d1
        txaio.add_callbacks(d2, notify_disconnect, None)

        def _error(e):
            return self._swallow_error(e, "While firing onDisconnect")
        txaio.add_callbacks(d2, None, _error)

    def onChallenge(self, challenge):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.onChallenge`
        """
        raise Exception("received authentication challenge, but onChallenge not implemented")

    def onJoin(self, details):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.onJoin`
        """

    def onLeave(self, details):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.onLeave`
        """
        if details.reason.startswith('wamp.error.'):
            self.log.error('{reason}: {wamp_message}', reason=details.reason, wamp_message=details.message)
        if self._transport:
            self.disconnect()
        # do we ever call onLeave with a valid transport?

    def leave(self, reason=None, log_message=None):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.leave`
        """
        if not self._session_id:
            raise Exception("not joined")

        if not self._goodbye_sent:
            if not reason:
                reason = u"wamp.close.normal"
            msg = wamp.message.Goodbye(reason=reason, message=log_message)
            self._transport.send(msg)
            self._goodbye_sent = True

            # deferred that fires when transport actually hits CLOSED
            is_closed = self._transport is None or self._transport.is_closed
            return is_closed
        else:
            raise SessionNotReady(u"Already requested to close the session")

    def onDisconnect(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.onDisconnect`
        """

    def publish(self, topic, *args, **kwargs):
        """
        Implements :func:`autobahn.wamp.interfaces.IPublisher.publish`
        """
        if six.PY2 and type(topic) == str:
            topic = six.u(topic)
        assert(type(topic) == six.text_type)

        if not self._transport:
            raise exception.TransportLost()

        request_id = self._request_id_gen.next()

        if 'options' in kwargs and isinstance(kwargs['options'], types.PublishOptions):
            options = kwargs.pop('options')
            msg = message.Publish(request_id, topic, args=args, kwargs=kwargs, **options.message_attr())
        else:
            options = None
            msg = message.Publish(request_id, topic, args=args, kwargs=kwargs)

        if options and options.acknowledge:
            # only acknowledged publications expect a reply ..
            on_reply = txaio.create_future()
            self._publish_reqs[request_id] = PublishRequest(request_id, on_reply)
        else:
            on_reply = None

        try:
            # Notes:
            #
            # * this might raise autobahn.wamp.exception.SerializationError
            #   when the user payload cannot be serialized
            # * we have to setup a PublishRequest() in _publish_reqs _before_
            #   calling transpor.send(), because a mock- or side-by-side transport
            #   will immediately lead on an incoming WAMP message in onMessage()
            #
            self._transport.send(msg)
        except Exception as e:
            if request_id in self._publish_reqs:
                del self._publish_reqs[request_id]
            raise e

        return on_reply

    def subscribe(self, handler, topic=None, options=None):
        """
        Implements :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`
        """
        assert((callable(handler) and topic is not None) or hasattr(handler, '__class__'))
        if topic and six.PY2 and type(topic) == str:
            topic = six.u(topic)
        assert(topic is None or type(topic) == six.text_type)
        assert(options is None or isinstance(options, types.SubscribeOptions))

        if not self._transport:
            raise exception.TransportLost()

        def _subscribe(obj, fn, topic, options):
            request_id = self._request_id_gen.next()
            on_reply = txaio.create_future()
            handler_obj = Handler(fn, obj, options.details_arg if options else None)
            self._subscribe_reqs[request_id] = SubscribeRequest(request_id, on_reply, handler_obj)

            if options:
                msg = message.Subscribe(request_id, topic, **options.message_attr())
            else:
                msg = message.Subscribe(request_id, topic)

            self._transport.send(msg)
            return on_reply

        if callable(handler):
            # subscribe a single handler
            return _subscribe(None, handler, topic, options)

        else:

            # subscribe all methods on an object decorated with "wamp.subscribe"
            on_replies = []
            for k in inspect.getmembers(handler.__class__, is_method_or_function):
                proc = k[1]
                if "_wampuris" in proc.__dict__:
                    for pat in proc.__dict__["_wampuris"]:
                        if pat.is_handler():
                            uri = pat.uri()
                            subopts = options or pat.subscribe_options()
                            on_replies.append(_subscribe(handler, proc, uri, subopts))

            # XXX needs coverage
            return txaio.gather(on_replies, consume_exceptions=True)

    def _unsubscribe(self, subscription):
        """
        Called from :meth:`autobahn.wamp.protocol.Subscription.unsubscribe`
        """
        assert(isinstance(subscription, Subscription))
        assert subscription.active
        assert(subscription.id in self._subscriptions)
        assert(subscription in self._subscriptions[subscription.id])

        if not self._transport:
            raise exception.TransportLost()

        # remove handler subscription and mark as inactive
        self._subscriptions[subscription.id].remove(subscription)
        subscription.active = False

        # number of handler subscriptions left ..
        scount = len(self._subscriptions[subscription.id])

        if scount == 0:
            # if the last handler was removed, unsubscribe from broker ..
            request_id = self._request_id_gen.next()

            on_reply = txaio.create_future()
            self._unsubscribe_reqs[request_id] = UnsubscribeRequest(request_id, on_reply, subscription.id)

            msg = message.Unsubscribe(request_id, subscription.id)

            self._transport.send(msg)
            return on_reply
        else:
            # there are still handlers active on the subscription!
            return txaio.create_future_success(scount)

    def call(self, procedure, *args, **kwargs):
        """
        Implements :func:`autobahn.wamp.interfaces.ICaller.call`
        """
        if six.PY2 and type(procedure) == str:
            procedure = six.u(procedure)
        assert(isinstance(procedure, six.text_type))

        if not self._transport:
            raise exception.TransportLost()

        request_id = self._request_id_gen.next()

        if 'options' in kwargs and isinstance(kwargs['options'], types.CallOptions):
            options = kwargs.pop('options')
            msg = message.Call(request_id, procedure, args=args, kwargs=kwargs, **options.message_attr())
        else:
            options = None
            msg = message.Call(request_id, procedure, args=args, kwargs=kwargs)

        # FIXME
        # def canceller(_d):
        #   cancel_msg = message.Cancel(request)
        #   self._transport.send(cancel_msg)
        # d = Deferred(canceller)

        on_reply = txaio.create_future()
        self._call_reqs[request_id] = CallRequest(request_id, on_reply, options)

        try:
            # Notes:
            #
            # * this might raise autobahn.wamp.exception.SerializationError
            #   when the user payload cannot be serialized
            # * we have to setup a PublishRequest() in _publish_reqs _before_
            #   calling transpor.send(), because a mock- or side-by-side transport
            #   will immediately lead on an incoming WAMP message in onMessage()
            #
            self._transport.send(msg)
        except:
            if request_id in self._call_reqs:
                del self._call_reqs[request_id]
            raise

        return on_reply

    def register(self, endpoint, procedure=None, options=None):
        """
        Implements :func:`autobahn.wamp.interfaces.ICallee.register`
        """
        if not callable(endpoint):
            raise RuntimeError("'endpoint' argument must be a callable")
        if procedure is None and not hasattr(endpoint, '__class__'):
            raise RuntimeError("Must specify a 'procedure' if endpoint isn't an instance")
        assert((callable(endpoint) and procedure is not None) or hasattr(endpoint, '__class__'))
        if procedure and six.PY2 and type(procedure) == str:
            procedure = six.u(procedure)
        assert(procedure is None or type(procedure) == six.text_type)
        assert(options is None or isinstance(options, types.RegisterOptions))

        if not self._transport:
            raise exception.TransportLost()

        def _register(obj, fn, procedure, options):
            request_id = self._request_id_gen.next()
            on_reply = txaio.create_future()
            endpoint_obj = Endpoint(fn, obj, options.details_arg if options else None)
            self._register_reqs[request_id] = RegisterRequest(request_id, on_reply, procedure, endpoint_obj)

            if options:
                msg = message.Register(request_id, procedure, **options.message_attr())
            else:
                msg = message.Register(request_id, procedure)

            self._transport.send(msg)
            return on_reply

        if callable(endpoint):

            # register a single callable
            return _register(None, endpoint, procedure, options)

        else:

            # register all methods on an object decorated with "wamp.register"
            on_replies = []
            for k in inspect.getmembers(endpoint.__class__, is_method_or_function):
                proc = k[1]
                if "_wampuris" in proc.__dict__:
                    for pat in proc.__dict__["_wampuris"]:
                        if pat.is_endpoint():
                            uri = pat.uri()
                            on_replies.append(_register(endpoint, proc, uri, options))

            # XXX neds coverage
            return txaio.gather(on_replies, consume_exceptions=True)

    def _unregister(self, registration):
        """
        Called from :meth:`autobahn.wamp.protocol.Registration.unregister`
        """
        assert(isinstance(registration, Registration))
        assert registration.active
        assert(registration.id in self._registrations)

        if not self._transport:
            raise exception.TransportLost()

        request_id = self._request_id_gen.next()

        on_reply = txaio.create_future()
        self._unregister_reqs[request_id] = UnregisterRequest(request_id, on_reply, registration.id)

        msg = message.Unregister(request_id, registration.id)

        self._transport.send(msg)
        return on_reply


# IApplicationSession.register collides with the abc.ABCMeta.register method
# IApplicationSession.register(ApplicationSession)


class ApplicationSessionFactory(object):
    """
    WAMP endpoint session factory.
    """

    session = ApplicationSession
    """
   WAMP application session class to be used in this factory.
   """

    def __init__(self, config=None):
        """

        :param config: The default component configuration.
        :type config: instance of :class:`autobahn.wamp.types.ComponentConfig`
        """
        self.config = config or types.ComponentConfig(realm=u"default")

    def __call__(self):
        """
        Creates a new WAMP application session.

        :returns: -- An instance of the WAMP application session class as
                     given by `self.session`.
        """
        session = self.session(self.config)
        session.factory = self
        return session
