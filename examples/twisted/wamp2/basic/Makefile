server:
	PYTHONPATH=../../../../autobahn python server.py


server_with_timeservice_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.timeservice.TimeServiceBackend"

client_timeservice_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.timeservice.TimeServiceFrontend"

client_timeservice_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.timeservice.TimeServiceBackend"


server_with_errors_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.errors.ErrorsTestBackend"

client_errors_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.errors.ErrorsTestFrontend"

client_errors_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.errors.ErrorsTestBackend"


server_with_pubsub_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "pubsub.pubsub.PubSubTestBackend"

client_pubsub_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.pubsub.PubSubTestFrontend"

client_pubsub_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.pubsub.PubSubTestBackend"


server_with_complexevent_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "pubsub.complexevent.ComplexEventTestBackend"

client_complexevent_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.complexevent.ComplexEventTestFrontend"

client_complexevent_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.complexevent.ComplexEventTestBackend"
