s1:
	PYTHONPATH=../../autobahn python -s test.py server ws://127.0.0.1:9000

broker1:
	PYTHONPATH=../../autobahn python ./pubsub/server.py

brokerclient1:
	PYTHONPATH=../../autobahn python ./pubsub/client.py --period 1

brokerclient2:
	PYTHONPATH=../../autobahn python ./pubsub/client.py --period 0

ser1:
	PYTHONPATH=../../autobahn python -s test_serializer.py server ws://127.0.0.1:9000

http1:
	PYTHONPATH=../../autobahn python ./longpoll/server.py

test3:
	PYTHONPATH=../../../autobahn python ./test3.py

test1_server:
	PYTHONPATH=../../../autobahn python ./test1/server.py

test1_client:
	PYTHONPATH=../../../autobahn python ./test1/client.py foobar1

test1b_client:
	PYTHONPATH=../../../autobahn python ./test1/client.py foobar2
