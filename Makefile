test:
	PYTHONPATH=./autobahn trial.py autobahn/autobahn/wamp2/tests/test_interfaces.py

testp:
	PYTHONPATH=./autobahn python autobahn/autobahn/wamp2/tests/test_interfaces.py
