all:
	@echo "Targets:"
	@echo ""
	@echo "   clean            Cleanup"
	@echo "   install          Local install"
	@echo "   publish          Clean build, register and publish to PyPi"
	@echo "   test             Run unit tests"
	@echo ""

install:
	#python setup.py install
#	pip install -e .[twisted]
#	pip install -e .[asyncio,twisted,accelerate,compress,serialization]
	pip install -e .[asyncio,twisted,accelerate,serialization]

clean:
	rm -rf ./autobahn.egg-info
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./temp
	rm -rf ./_trial_temp
	rm -rf ./.tox
	find . -name "*.tar.gz" -type f -exec rm -f {} \;
	find . -name "*.egg" -type f -exec rm -f {} \;
	find . -name "*.pyc" -type f -exec rm -f {} \;
	find . -name "*__pycache__" -type d -exec rm -rf {} \;

publish: clean
	python setup.py register
	python setup.py sdist upload

test:
	USE_TWISTED=1 trial autobahn

test1:
	USE_TWISTED=1 trial autobahn.wamp.test.test_auth
#	USE_TWISTED=1 python -m pytest -s -v autobahn/wamp/test/test_auth.py
#	USE_TWISTED=1 python -m pytest -s -v autobahn/wamp/test/test_router.py
#	USE_ASYNCIO=1 python -m pytest -s -v autobahn/wamp/test/test_router.py

test2:
#	USE_TWISTED=1 python -m pytest -s -v autobahn/wamp/test/test_router.py
	USE_ASYNCIO=1 python -m pytest -s -v autobahn/wamp/test/test_router.py
#	trial autobahn
#	trial autobahn.websocket.test
#	trial autobahn.wamp.test
#	trial autobahn.wamp.test.test_component
#	trial autobahn.wamp.test.test_message
#	trial autobahn.wamp.test.test_protocol
#	trial autobahn.wamp.test.test_protocol_peer
#	trial autobahn.wamp.test.test_serializer
#	trial autobahn.wamp.test.test_uri_pattern

pyflakes:
	pyflakes .

pep8:
	pep8 --statistics -qq
# pep8 --select=E231 --show-source

autopep8:
	autopep8 -ri --aggressive .
