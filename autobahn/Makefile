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
	trial.py autobahn.wamp.tests
#	trial.py autobahn.wamp.tests.test_message
#	trial.py autobahn.wamp.tests.test_protocol
#	trial.py autobahn.wamp.tests.test_protocol_peer
#	trial.py autobahn.wamp.tests.test_serializer
#	trial.py autobahn.wamp.tests.test_uri_pattern
