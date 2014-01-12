all:
	@echo "Targets:"
	@echo ""
	@echo "   clean            Cleanup"
	@echo "   install          Local install"
	@echo "   publish          Clean build, register and publish to PyPi"
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
	python3 setup.py register
	python3 setup.py sdist upload

test:
	trial.py autobahn.wamp.tests
#	trial.py autobahn.wamp.tests.test_message
#	trial.py autobahn.wamp.tests.test_uri_pattern

testp:
	python -m autobahn.wamp.tests.test_message
#	python autobahn/wamp/tests/test_message.py
#	python autobahn/wamp2/tests/test_uri_pattern.py
