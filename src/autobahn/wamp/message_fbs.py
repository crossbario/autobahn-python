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

from autobahn import flatbuffers

# Message type and enums
from autobahn.wamp.gen.wamp.proto import Message
from autobahn.wamp.gen.wamp.proto.MessageType import MessageType

# Enums used by message build() methods
from autobahn.wamp.gen.wamp.proto.Match import Match
from autobahn.wamp.gen.wamp.proto.InvocationPolicy import InvocationPolicy
from autobahn.wamp.gen.wamp.proto.CancelMode import CancelMode

# Category 1: Session lifecycle messages (neither payload nor forwarding)
from autobahn.wamp.gen.wamp.proto import Hello as HelloGen
from autobahn.wamp.gen.wamp.proto import Welcome as WelcomeGen
from autobahn.wamp.gen.wamp.proto import Abort as AbortGen
from autobahn.wamp.gen.wamp.proto import Challenge as ChallengeGen
from autobahn.wamp.gen.wamp.proto import Authenticate as AuthenticateGen
from autobahn.wamp.gen.wamp.proto import Goodbye as GoodbyeGen

# Category 1: PubSub messages (neither payload nor forwarding)
from autobahn.wamp.gen.wamp.proto import Subscribe as SubscribeGen
from autobahn.wamp.gen.wamp.proto import Subscribed as SubscribedGen
from autobahn.wamp.gen.wamp.proto import Unsubscribe as UnsubscribeGen
from autobahn.wamp.gen.wamp.proto import Unsubscribed as UnsubscribedGen
from autobahn.wamp.gen.wamp.proto import Published as PublishedGen

# Category 1: RPC messages (neither payload nor forwarding)
from autobahn.wamp.gen.wamp.proto import Register as RegisterGen
from autobahn.wamp.gen.wamp.proto import Registered as RegisteredGen
from autobahn.wamp.gen.wamp.proto import Unregister as UnregisterGen
from autobahn.wamp.gen.wamp.proto import Unregistered as UnregisteredGen

# Category 3: Forwarding only messages
from autobahn.wamp.gen.wamp.proto import EventReceived as EventReceivedGen
from autobahn.wamp.gen.wamp.proto import Cancel as CancelGen
from autobahn.wamp.gen.wamp.proto import Interrupt as InterruptGen

# Category 4: Both Payload and Forwarding messages
from autobahn.wamp.gen.wamp.proto import Error as ErrorGen
from autobahn.wamp.gen.wamp.proto import Event as EventGen
from autobahn.wamp.gen.wamp.proto import Publish as PublishGen
from autobahn.wamp.gen.wamp.proto import Call as CallGen
from autobahn.wamp.gen.wamp.proto import Result as ResultGen
from autobahn.wamp.gen.wamp.proto import Invocation as InvocationGen
from autobahn.wamp.gen.wamp.proto import Yield as YieldGen

__all__ = (
    "Event",
    "Publish",
    "Error",
    "Call",
    "Result",
    "Invocation",
    "Yield",
    "Message",
    "MessageType",
    "Match",
    "InvocationPolicy",
    "CancelMode",
    "HelloGen",
    "WelcomeGen",
    "AbortGen",
    "ChallengeGen",
    "AuthenticateGen",
    "GoodbyeGen",
    "SubscribeGen",
    "SubscribedGen",
    "UnsubscribeGen",
    "UnsubscribedGen",
    "PublishedGen",
    "RegisterGen",
    "RegisteredGen",
    "UnregisterGen",
    "UnregisteredGen",
    "EventReceivedGen",
    "CancelGen",
    "InterruptGen",
    "ErrorGen",
    "CallGen",
    "ResultGen",
    "InvocationGen",
    "YieldGen",
    "PublishGen",
)


class Event(EventGen.Event):
    @classmethod
    def GetRootAsEvent(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Event()
        x.Init(buf, n + offset)
        return x

    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    def ArgsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def KwargsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def PayloadAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def EncKeyAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None


class Publish(PublishGen.Publish):
    @classmethod
    def GetRootAsEvent(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Event()
        x.Init(buf, n + offset)
        return x

    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    def ArgsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def KwargsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def PayloadAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def EncKeyAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None


class Error(ErrorGen.Error):
    @classmethod
    def GetRootAsError(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Error()
        x.Init(buf, n + offset)
        return x

    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    def ArgsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def KwargsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def PayloadAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def EncKeyAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(22))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None


class Call(CallGen.Call):
    @classmethod
    def GetRootAsCall(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Call()
        x.Init(buf, n + offset)
        return x

    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    def ArgsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def KwargsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def PayloadAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def EncKeyAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(22))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None


class Result(ResultGen.Result):
    @classmethod
    def GetRootAsResult(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Result()
        x.Init(buf, n + offset)
        return x

    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    def ArgsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def KwargsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def PayloadAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def EncKeyAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(22))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None


class Invocation(InvocationGen.Invocation):
    @classmethod
    def GetRootAsInvocation(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Invocation()
        x.Init(buf, n + offset)
        return x

    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    def ArgsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def KwargsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def PayloadAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def EncKeyAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(26))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None


class Yield(YieldGen.Yield):
    @classmethod
    def GetRootAsYield(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Yield()
        x.Init(buf, n + offset)
        return x

    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    def ArgsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def KwargsAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def PayloadAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None

    def EncKeyAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off : _off + _len]
        return None
