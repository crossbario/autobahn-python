all:
	@echo "Targets:"
	@echo ""
	@echo "   clean            Cleanup"
	@echo "   install          Local install"
	@echo "   publish          Clean build, register and publish to PyPi"
	@echo "   test             Run unit tests"
	@echo ""

install:
	python setup.py install

clean:
	rm -rf ./autobahn.egg-info
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./temp
	find . -name "*.tar.gz" -type f -exec rm -f {} \;
	find . -name "*.egg" -type f -exec rm -f {} \;
	find . -name "*.pyc" -type f -exec rm -f {} \;
	find . -name "*__pycache__" -type d -exec rm -rf {} \;

publish: clean
	python setup.py register
	python setup.py sdist upload

test:
	trial autobahn.wamp.test.test_component
#	trial autobahn
#	trial autobahn.websocket.test
#	trial autobahn.wamp.test
#	trial autobahn.wamp.test.test_message
#	trial autobahn.wamp.test.test_protocol
#	trial autobahn.wamp.test.test_protocol_peer
#	trial autobahn.wamp.test.test_serializer
#	trial autobahn.wamp.test.test_uri_pattern
