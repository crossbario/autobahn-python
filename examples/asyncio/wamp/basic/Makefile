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


s:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py


s1:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "rpc.timeservice.backend.Component"

f1:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.timeservice.frontend.Component"

b1:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.timeservice.backend.Component"


s2:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "rpc.slowsquare.backend.Component"

f2:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.slowsquare.frontend.Component"

b2:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.slowsquare.backend.Component"


s3:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "rpc.arguments.backend.Component"

f3:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.arguments.frontend.Component"

b3:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.arguments.backend.Component"


s4:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "rpc.options.backend.Component"

f4:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.options.frontend.Component"

b4:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.options.backend.Component"


s5:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "rpc.errors.backend.Component"

f5:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.errors.frontend.Component"

b5:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.errors.backend.Component"


s6:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "rpc.complex.backend.Component"

f6:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.complex.frontend.Component"

b6:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.complex.backend.Component"


s7:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "rpc.progress.backend.Component"

f7:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.progress.frontend.Component"

b7:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.progress.backend.Component"


s8:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "rpc.decorators.backend.Component"

f8:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.decorators.frontend.Component"

b8:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "rpc.decorators.backend.Component"


s9:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "pubsub.basic.backend.Component"

f9:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "pubsub.basic.frontend.Component"

b9:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "pubsub.basic.backend.Component"


s10:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "pubsub.complex.backend.Component"

f10:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "pubsub.complex.frontend.Component"

b10:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "pubsub.complex.backend.Component"


s11:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "pubsub.options.backend.Component"

f11:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "pubsub.options.frontend.Component"

b11:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "pubsub.options.backend.Component"


s12:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "pubsub.unsubscribe.backend.Component"

f12:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "pubsub.unsubscribe.frontend.Component"

b12:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "pubsub.unsubscribe.backend.Component"


s13:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "pubsub.decorators.backend.Component"

f13:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "pubsub.decorators.frontend.Component"

b13:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "pubsub.decorators.backend.Component"


s14:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 server.py --component "session.series.backend.Component"

f14:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "session.series.frontend.Component"

b14:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 client.py --component "session.series.backend.Component"


client_session_fromoutside_backend:
	PYTHONPATH=../../../../autobahn ~/python34/bin/python3 session/fromoutside/backend.py
