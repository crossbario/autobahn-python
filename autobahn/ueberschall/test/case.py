##############################################################################
##
# Crossbar.io Fabric ("Ueberschall")
# Copyright (C) Crossbar.io Technologies GmbH. All rights reserved.
##
##############################################################################

import pickle

from autobahn.websocket.protocol import WebSocketProtocol


class Case:

    FAILED = "FAILED"
    OK = "OK"
    NON_STRICT = "NON-STRICT"
    WRONG_CODE = "WRONG CODE"
    UNCLEAN = "UNCLEAN"
    FAILED_BY_CLIENT = "FAILED BY CLIENT"
    INFORMATIONAL = "INFORMATIONAL"
    UNIMPLEMENTED = "UNIMPLEMENTED"

    # to remove
    NO_CLOSE = "NO_CLOSE"

    SUBCASES = []

    def __init__(self, protocol):
        self.p = protocol
        self.received = []
        self.expected = {}
        self.expectedClose = {}
        self.behavior = Case.FAILED
        self.behaviorClose = Case.FAILED
        self.result = "Actual events differ from any expected."
        self.resultClose = "TCP connection was dropped without close handshake"
        self.reportTime = False
        self.reportCompressionRatio = False
        self.trafficStats = None
        self.subcase = None
        # suppresses automatic close behavior (used in cases that deliberately
        # send bad close behavior)
        self.suppressClose = False

        # defaults for permessage-deflate - will be overridden in
        # permessage-deflate test cases (but only for those)
        ##
        self.perMessageDeflate = False
        self.perMessageDeflateOffers = []
        self.perMessageDeflateAccept = lambda connectionRequest, acceptNoContextTakeover, acceptMaxWindowBits, requestNoContextTakeover, requestMaxWindowBits: None

        self.init()

    def getSubcaseCount(self):
        return len(Case.SUBCASES)

    def setSubcase(self, subcase):
        self.subcase = subcase

    def init(self):
        pass

    def onOpen(self):
        pass

    def onMessage(self, msg, binary):
        self.received.append(("message", msg, binary))
        self.finishWhenDone()

    def onPing(self, payload):
        self.received.append(("ping", payload))
        self.finishWhenDone()

    def onPong(self, payload):
        self.received.append(("pong", payload))
        self.finishWhenDone()

    def onClose(self, wasClean, code, reason):
        pass

    def compare(self, obj1, obj2):
        return pickle.dumps(obj1) == pickle.dumps(obj2)

    def onConnectionLost(self, failedByMe):
        # check if we passed the test
        for e in self.expected:
            if self.compare(self.received, self.expected[e]):
                self.behavior = e
                self.passed = True
                self.result = "Actual events match at least one expected."
                break

        if self.p.connectionWasOpen:
            # check the close status
            if self.expectedClose["closedByMe"] != self.p.closedByMe:
                self.behaviorClose = Case.FAILED
                self.resultClose = "The connection was failed by the wrong endpoint"
            elif self.expectedClose["requireClean"] and not self.p.wasClean:
                self.behaviorClose = Case.UNCLEAN
                self.resultClose = "The spec requires the connection to be failed cleanly here"
            elif self.p.remoteCloseCode is not None and self.p.remoteCloseCode not in self.expectedClose["closeCode"]:
                self.behaviorClose = Case.WRONG_CODE
                self.resultClose = "The close code should have been %s or empty" % ','.join(
                    map(str, self.expectedClose["closeCode"]))
            elif not self.p.factory.isServer and self.p.droppedByMe:
                self.behaviorClose = Case.FAILED_BY_CLIENT
                self.resultClose = "It is preferred that the server close the TCP connection"
            else:
                self.behaviorClose = Case.OK
                self.resultClose = "Connection was properly closed"

            # for UTF8 tests, closing by wrong endpoint means case failure, since
            # the peer then did not detect the invalid UTF8 at all
            ##
            closedByWrongEndpointIsFatal = self.expectedClose.get(
                "closedByWrongEndpointIsFatal", False)
            if closedByWrongEndpointIsFatal and self.expectedClose["closedByMe"] != self.p.closedByMe:
                self.behavior = Case.FAILED
        else:
            self.behaviorClose = Case.FAILED
            self.resultClose = "The WebSocket opening handshake was never completed!"

    def finishWhenDone(self):
        # if we match at least one expected outcome check if we are supposed to
        # start the closing handshake and if so, do it.
        for e in self.expected:
            if not self.compare(self.received, self.expected[e]):
                return
        if self.expectedClose["closedByMe"] and not self.suppressClose:
            self.p.sendClose(self.expectedClose["closeCode"][0])
