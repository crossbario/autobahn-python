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
	@echo "RPC Slow Square:"
	@echo "   server_with_rpc_slowsquare_backend"
	@echo "   client_rpc_slowsquare_frontend"
	@echo "   client_rpc_slowsquare_backend"
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
	@echo "RPC Decorators:"
	@echo "   server_with_rpc_decorators_backend"
	@echo "   client_rpc_decorators_frontend"
	@echo "   client_rpc_decorators_backend"
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
	@echo "PubSub Unsubscribe:"
	@echo "   server_with_pubsub_unsubscribe_backend"
	@echo "   client_pubsub_unsubscribe_frontend"
	@echo "   client_pubsub_unsubscribe_backend"
	@echo ""
	@echo "PubSub Decorators:"
	@echo "   server_with_pubsub_decorators_backend"
	@echo "   client_pubsub_decorators_frontend"
	@echo "   client_pubsub_decorators_backend"
	@echo ""
	@echo "Session Series:"
	@echo "   server_with_session_series_backend"
	@echo "   client_session_series_frontend"
	@echo "   client_session_series_backend"
	@echo ""


server:
	PYTHONPATH=../../../../autobahn python server.py


server_with_rpc_timeservice_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.timeservice.backend.Component"

client_rpc_timeservice_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.timeservice.frontend.Component"

client_rpc_timeservice_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.timeservice.backend.Component"


server_with_rpc_slowsquare_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.slowsquare.backend.Component"

client_rpc_slowsquare_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.slowsquare.frontend.Component"

client_rpc_slowsquare_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.slowsquare.backend.Component"


server_with_rpc_arguments_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.arguments.backend.Component"

client_rpc_arguments_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.arguments.frontend.Component"

client_rpc_arguments_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.arguments.backend.Component"


server_with_rpc_options_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.options.backend.Component"

client_rpc_options_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.options.frontend.Component"

client_rpc_options_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.options.backend.Component"


server_with_rpc_errors_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.errors.backend.Component"

client_rpc_errors_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.errors.frontend.Component"

client_rpc_errors_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.errors.backend.Component"


server_with_rpc_complex_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.complex.backend.Component"

client_rpc_complex_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.complex.frontend.Component"

client_rpc_complex_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.complex.backend.Component"


server_with_rpc_progress_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.progress.backend.Component"

client_rpc_progress_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.progress.frontend.Component"

client_rpc_progress_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.progress.backend.Component"


server_with_rpc_decorators_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "rpc.decorators.backend.Component"

client_rpc_decorators_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.decorators.frontend.Component"

client_rpc_decorators_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "rpc.decorators.backend.Component"


server_with_pubsub_basic_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "pubsub.basic.backend.Component"

client_pubsub_basic_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.basic.frontend.Component"

client_pubsub_basic_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.basic.backend.Component"


server_with_pubsub_complex_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "pubsub.complex.backend.Component"

client_pubsub_complex_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.complex.frontend.Component"

client_pubsub_complex_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.complex.backend.Component"


server_with_pubsub_options_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "pubsub.options.backend.Component"

client_pubsub_options_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.options.frontend.Component"

client_pubsub_options_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.options.backend.Component"


server_with_pubsub_unsubscribe_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "pubsub.unsubscribe.backend.Component"

client_pubsub_unsubscribe_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.unsubscribe.frontend.Component"

client_pubsub_unsubscribe_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.unsubscribe.backend.Component"


server_with_pubsub_decorators_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "pubsub.decorators.backend.Component"

client_pubsub_decorators_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.decorators.frontend.Component"

client_pubsub_decorators_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "pubsub.decorators.backend.Component"


server_with_session_series_backend:
	PYTHONPATH=../../../../autobahn python server.py --component "session.series.backend.Component"

client_session_series_frontend:
	PYTHONPATH=../../../../autobahn python client.py --component "session.series.frontend.Component"

client_session_series_backend:
	PYTHONPATH=../../../../autobahn python client.py --component "session.series.backend.Component"
