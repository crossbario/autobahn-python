import binascii

from autobahn.wamp.serializer import JsonObjectSerializer, MsgPackObjectSerializer

# ser = JsonObjectSerializer(batched = True)
ser = MsgPackObjectSerializer(batched=True)


o1 = [1, "hello", [1, 2, 3]]
o2 = [3, {"a": 23, "b": 24}]

d1 = ser.serialize(o1) + ser.serialize(o2) + ser.serialize(o1)

m = ser.unserialize(d1)

print m
