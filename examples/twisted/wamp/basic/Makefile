all:
	@echo "Targets:"
	@echo ""
	@echo "Router-only:"
	@echo "   server"
	@echo ""
	@echo "RPC Time Service:"
	@echo "   server_with_rpc_timeservice_backend"
	@echo "   client_rpc_timeservice_frontend"
	@echo "   client_rpc_timeservice_backend"
	@echo ""
	@echo "RPC Arguments:"
	@echo "   server_with_rpc_arguments_backend"
	@echo "   client_rpc_arguments_frontend"
	@echo "   client_rpc_arguments_backend"
	@echo ""
	@echo "RPC Options:"
	@echo "   server_with_rpc_options_backend"
	@echo "   client_rpc_options_frontend"
	@echo "   client_rpc_options_backend"
	@echo ""
	@echo "RPC Errors:"
	@echo "   server_with_rpc_errors_backend"
	@echo "   client_rpc_errors_frontend"
	@echo "   client_rpc_errors_backend"
	@echo ""
	@echo "RPC Complex Result:"
	@echo "   server_with_rpc_complex_backend"
	@echo "   client_rpc_complex_frontend"
	@echo "   client_rpc_complex_backend"
	@echo ""
	@echo "RPC Progressive Results:"
	@echo "   server_with_rpc_progress_backend"
	@echo "   client_rpc_progress_frontend"
	@echo "   client_rpc_progress_backend"
	@echo ""
	@echo "PubSub Basic:"
	@echo "   server_with_pubsub_basic_backend"
	@echo "   client_pubsub_basic_frontend"
	@echo "   client_pubsub_basic_backend"
	@echo ""
	@echo "PubSub Complex Event:"
	@echo "   server_with_pubsub_complex_backend"
	@echo "   client_pubsub_complex_frontend"
	@echo "   client_pubsub_complex_backend"
	@echo ""
	@echo "PubSub Options:"
	@echo "   server_with_pubsub_options_backend"
	@echo "   client_pubsub_options_frontend"
	@echo "   client_pubsub_options_backend"
	@echo ""


server:
	PYTHONPATH=../../../../autobahn python server.py


server_with_rpc_timeservice_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.timeservice.TimeServiceBackend"

client_rpc_timeservice_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.timeservice.TimeServiceFrontend"

client_rpc_timeservice_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.timeservice.TimeServiceBackend"


server_with_rpc_arguments_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.arguments.ArgumentsBackend"

client_rpc_arguments_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.arguments.ArgumentsFrontend"

client_rpc_arguments_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.arguments.ArgumentsBackend"


server_with_rpc_options_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.rpcoptions.RpcOptionsBackend"

client_rpc_options_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.rpcoptions.RpcOptionsFrontend"

client_rpc_options_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.rpcoptions.RpcOptionsBackend"


server_with_rpc_errors_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.errors.ErrorsTestBackend"

client_rpc_errors_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.errors.ErrorsTestFrontend"

client_rpc_errors_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.errors.ErrorsTestBackend"


server_with_rpc_complex_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.complex.ComplexBackend"

client_rpc_complex_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.complex.ComplexFrontend"

client_rpc_complex_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.complex.ComplexBackend"


server_with_rpc_progress_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.progress.ProgressiveBackend"

client_rpc_progress_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.progress.ProgressiveFrontend"

client_rpc_progress_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.progress.ProgressiveBackend"


server_with_pubsub_basic_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "pubsub.pubsub.PubSubTestBackend"

client_pubsub_basic_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.pubsub.PubSubTestFrontend"

client_pubsub_basic_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.pubsub.PubSubTestBackend"


server_with_pubsub_complex_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "pubsub.complexevent.ComplexEventTestBackend"

client_pubsub_complex_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.complexevent.ComplexEventTestFrontend"

client_pubsub_complex_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.complexevent.ComplexEventTestBackend"


server_with_pubsub_options_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "pubsub.pubsuboptions.PubSubOptionsTestBackend"

client_pubsub_options_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.pubsuboptions.PubSubOptionsTestFrontend"

client_pubsub_options_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.pubsuboptions.PubSubOptionsTestBackend"
