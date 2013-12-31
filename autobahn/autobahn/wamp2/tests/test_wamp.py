###############################################################################
##
##  Copyright 2011,2012,2013 Tavendo GmbH
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

"""Unit tests for the WAMP protocol.

This module provides unit tests for classes in wamp.py.

Usage: Run `trial tests/test_wamp.py` in the autobahn/autobahn directory.
"""

from twisted.internet import defer
from twisted.trial import unittest

import websocket
import wamp
import prefixmap


CALL_ID = "0123456789ABCDEF"
URI = "http://wamp.ws"


class MockFactory(object):

    msg = []

    def _serialize(self, msg):
        self.msg = msg
        return "<<%s>>" % msg



def dummyRpc():
    return "Yummy!" # Not a deferred



class MockProto(object):
    """
    A mock protocol used for instantiating the handlers.
    Provides all instance variables and methods needed by
    the handlers.
    """


    def __init__(self):
        self.trackTimings = False
        self.trackedTimings = websocket.Timings()
        self.procs = {URI: (None, dummyRpc, False)}
        self.calls = {}
        self.factory = MockFactory()
        self.includeTraceback = True
        self.debugWamp = True


    def startTracking(self):
        self.trackTimings = True


    def stopTracking(self):
        self.trackTimings = False


    def doTrack(self, msg):
        self.trackedTimings.track(msg)


    def procForUri(self, uri):
        return self.procs[uri] if uri in self.procs else None


    def onBeforeCall(self, callid, uri, args, isRegistered):
        self.callid, self.uri, self.args, self.isRegistered = \
            callid, uri, args, isRegistered
        return uri, args


    def onAfterCallError(self, error, call):
        return error


    def onAfterCallSuccess(self, result, call):
        return result


    def onAfterSendCallError(self, msg, call):
        pass


    def onAfterSendCallSuccess(self, msg, call):
        pass


    def sendMessage(self, msg):
        self.msg = msg


    def _protocolError(self, msg):
        self.error_msg = msg


        
class AbstractHandlerTest(unittest.TestCase):


    def setUp(self):
        self.proto = MockProto()
        self.prefixMap = prefixmap.PrefixMap()
        self.handler = self.handler_cls(self.proto, self.prefixMap)
        self._origMsg = wamp.log.msg
        wamp.log.msg = self._storeLogMsg


    def tearDown(self):
        wamp.log.msg = self._origMsg


    def _storeResult(self, result):
        self.result = result


    def _storeLogMsg(self, *args, **kw):
        self.log_msg = args[0] if args else None


    def _storeException(self, failure):
        self.exc = failure.value


        
class TestHandler(AbstractHandlerTest):
    """
    Tests the abstract handler class.
    """

    handler_cls = wamp.Handler


    def setUp(self):
        AbstractHandlerTest.setUp(self)
        self.call = wamp.Call(self.proto, CALL_ID, URI, [])


    def testHandleMessage(self):
        """
        Messages can't be handled in the superclass.
        """
        dummyTypeId = 42 # If typeid is None, an assertion is raised ==>
        self.handler.typeid = dummyTypeId # ... assign a dummy value
        self.assertRaises(NotImplementedError,
                          self.handler.handleMessage, [dummyTypeId])


    def testHandleMessageTypecheckSingleTypeId(self):
        """
        If the provided type does not match self.typeid, an exception
        should be raised.
        """
        self.assertRaises(AssertionError,
                          self.handler.handleMessage, [42])


    def testHandleMessageTypecheckMultipleTypeIds(self):
        """
        If the provided type is not one of self.typeids, an exception
        should be raised.
        """
        self.handler.typeids = [1, 2]
        self.assertRaises(AssertionError,
                          self.handler.handleMessage, [42])


    def testMaybeTrackTimings(self):
        """
        If tracking is switched on, the handler should track timing info.
        """
        self.proto.startTracking()
        self.handler.maybeTrackTimings(self.call, "Track me, please")
        self.failUnless("Track me, please" in self.call.timings._timings)
        self.assertEquals(self.proto.trackedTimings._timings, {})


        
class TestCallHandler(AbstractHandlerTest):
    """
    Tests the handler for CALL messages.
    """

    typeid = wamp.WampProtocol.MESSAGE_TYPEID_CALL
    handler_cls = wamp.CallHandler


    def test_ParseMessageParts(self):
        """
        After parsing the message parts, call_id, uri and args should
        be set to the expected values.
        """
        self.handler._parseMessageParts([self.typeid, CALL_ID, URI])
        self.assertEqual(self.handler.callid, CALL_ID)
        self.assertEqual(self.handler.uri, URI)
        self.assertEqual(self.handler.args, [])


    def testDoHandleMessage(self):
        """
        After handling the message, a new message containing the type
        id, call id and call result should have been sent.  Uses the
        fact that `sendMessage` just stores the message as `msg`
        instance variable in the factory.
        """
        self.handler._parseMessageParts([self.typeid, CALL_ID, URI])
        self.handler._handleMessage()
        if len(self.proto.factory.msg) != 3:
            return
        typeid, callid, msg = self.proto.factory.msg
        self.assertEquals(typeid,
                          wamp.WampProtocol.MESSAGE_TYPEID_CALL_RESULT)
        self.assertEquals(callid, CALL_ID)
        self.assertEquals(msg, "Yummy!")


    def test_onBeforeCall(self):
        """
        The _onBeforeCall should instantiate a `Call` object with the
        appropriate instance variables.
        """
        self.handler._parseMessageParts([self.typeid, CALL_ID, URI])
        call = self.handler._onBeforeCall()
        self.assertEquals(call.proto, self.proto)
        self.assertEquals(call.callid, CALL_ID)
        self.assertEquals(call.uri, URI)
        self.assertEquals(call.args, [])
        self.assertEquals(call.extra, None)
        self.assertEquals(call.timings, None)


    def test_onBeforeCallTracking(self):
        """
        If tracking is enabled, onBeforeCall should create a `Timing`
        instance and assign it to the call that is returned.
        """
        self.proto.startTracking()
        self.handler._parseMessageParts([self.typeid, CALL_ID, URI])
        call = self.handler._onBeforeCall()
        self.failUnless(isinstance(call.timings, websocket.Timings))
        self.failUnless("onBeforeCall" in call.timings._timings)


    def test_callProcedure(self):
        """
        Calling the procedure `dummyRpc (connected to URI in the mock
        protocol) should return 'Yummy!'.
        """
        call = wamp.Call(self.proto, CALL_ID, URI, [])
        self.assertEquals(self.handler._callProcedure(call), "Yummy!")


        
class TestCallResultHandler(AbstractHandlerTest):
    """
    Tests the handler for CALL_RESULT messages
    """

    handler_cls = wamp.CallResultHandler


    def test_ParseMessageParts(self):
        """
        The call result handler should check the validity of the
        message and assign instance variables for call id and result.
        """
        self.handler._messageIsValid(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_RESULT])
        self.assertEquals(self.proto.error_msg,
                          "WAMP CALL_RESULT message without <callid>")
        self.handler._messageIsValid(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_RESULT, CALL_ID])
        self.assertEquals(self.proto.error_msg,
            "WAMP CALL_RESULT message with invalid length 2")
        self.handler._parseMessageParts(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_RESULT, CALL_ID, 0])
        self.assertEquals(self.handler.callid, CALL_ID)
        self.assertEquals(self.handler.result, 0)


    def test_HandleMessage(self):
        """
        When a call result message is received, the appropriate
        Deferred object should be called with the result.
        """
        d = defer.Deferred()
        d.addCallback(self._storeResult)
        self.proto.calls[CALL_ID] = d
        self.handler._parseMessageParts(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_RESULT, CALL_ID,
             0])
        self.handler._handleMessage()
        self.assertEquals(self.result, 0)


    def test_HandleMessageWithMissingDeferred(self):
        """
        If there is no Deferred object for the message's call id, a
        log message should be written (since the mock protocol's
        debugWamp is True).
        """
        self.handler._parseMessageParts(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_RESULT, CALL_ID,
             0])
        self.handler._handleMessage()
        self.assertEqual(self.log_msg,
            "callid not found for received call result message")



class TestCallErrorHandler(AbstractHandlerTest):
    """
    Tests the handler for CALL_ERROR messages
    """

    handler_cls = wamp.CallErrorHandler


    def test_ParseMessagePartsInvalid(self):
        """
        The structure of call error message should be checked.  If
        elements are missing or have the wrong type, an error should
        be sent. Errors are stored in the mock protocol's `error_msg`
        instance variable.
        """
        for i in range(4):
            self.handler._messageIsValid([0]*i)
            self.assertEqual(self.proto.error_msg,
                "call error message invalid length %d" % i)
        self.handler._messageIsValid(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_ERROR,
             CALL_ID, 0, ""])
        self.assertEqual(self.proto.error_msg,
                ("invalid type <type 'int'> for errorUri "
                 "in call error message"))
        self.handler._messageIsValid(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_ERROR,
             CALL_ID, "", 0])
        self.assertEqual(self.proto.error_msg,
                ("invalid type <type 'int'> for errorDesc "
                 "in call error message"))


    def test_ParseMessagePartsWithoutDetails(self):
        """
        Error details may be missing in a call error message.
        In this case, the `errordetails` instance variable
        should be set to None.
        """
        self.handler._parseMessageParts(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_ERROR,
             CALL_ID, URI, "desc"])
        self.assertEqual(self.handler.callid, CALL_ID)
        self.assertEqual(self.handler.erroruri, URI)
        self.assertEqual(self.handler.errordesc, "desc")
        self.assertEqual(self.handler.errordetails, None)


    def test_ParseMessagePartsWithDetails(self):
        """
        If error details are available, they should be stored in
        `errordetails`.
        """
        self.handler._parseMessageParts(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_ERROR,
             CALL_ID, URI, "desc", "details"])
        self.assertEqual(self.handler.callid, CALL_ID)
        self.assertEqual(self.handler.erroruri, URI)
        self.assertEqual(self.handler.errordesc, "desc")
        self.assertEqual(self.handler.errordetails, "details")


    def test_HandleMessage(self):
        """
        If an RPC call results in an error, the message should
        trigger the respective Deferred object's errback with
        an exception containing the error details in its `args`
        instance variable.

        We register the method `_storeException`, which stores the
        original exception (not the Failure) in `self.exc`.
        """
        d = defer.Deferred()
        d.addErrback(self._storeException)
        self.proto.calls[CALL_ID] = d
        self.handler._parseMessageParts(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_ERROR, CALL_ID,
             URI, "desc", "details"])
        self.handler._handleMessage()
        self.assertEquals(self.exc.args, (URI, "desc", "details"))


    def test_HandleMessageWithMissingDeferred(self):
        """
        If the peer sends an RPC call error message with an unknown
        call ID, the incident should be logged.
        """
        self.handler._parseMessageParts(
            [wamp.WampProtocol.MESSAGE_TYPEID_CALL_RESULT, CALL_ID,
             URI, "desc"])
        self.handler._handleMessage()
        self.assertEqual(self.log_msg,
            "callid not found for received call error message")

