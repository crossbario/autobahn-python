all:
	@echo "Targets:"
	@echo ""
	@echo "   clean            Cleanup"
	@echo "   install          Local install"
	@echo "   publish          Clean build, register and publish to PyPi"
	@echo "   test             Run unit tests"
	@echo "   flake8           Run flake8 code checking"
	@echo ""

# install locally
install:
	#python setup.py install
#	pip install -e .[twisted]
#	pip install -e .[asyncio,twisted,accelerate,compress,serialization]
	pip install --upgrade -e .[all,dev]

# cleanup everything
clean:
	rm -rf ./autobahn.egg-info
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./temp
	rm -rf ./_trial_temp
	rm -rf ./.tox
	rm -rf ./.eggs
	rm -f  ./twisted/plugins/dropin.cache
	find . -name "*.tar.gz" -type f -exec rm -f {} \;
	find . -name "*.egg" -type f -exec rm -f {} \;
	find . -name "*.pyc" -type f -exec rm -f {} \;
	find . -name "*__pycache__" -type d -exec rm -rf {} \;

# publish to PyPI
publish: clean
	python setup.py register
	python setup.py sdist upload

# direct test via pytest (only here because of setuptools test integration)
test_pytest:
	python -m pytest -rsx .

# test via setuptools command
test_setuptools:
	python setup.py test

# test under Twisted
test_twisted:
	USE_TWISTED=1 trial autobahn
	#WAMP_ROUTER_URL="ws://127.0.0.1:8080/ws" USE_TWISTED=1 trial autobahn

test_twisted_coverage:
	-rm .coverage
	USE_TWISTED=1 coverage run --omit=*/test/* --source=autobahn `which trial` autobahn
#	coverage -a -d annotated_coverage
	coverage html
	coverage report --show-missing

# test under asyncio
test_asyncio:
	USE_ASYNCIO=1 python -m pytest -rsx
	#WAMP_ROUTER_URL="ws://127.0.0.1:8080/ws" USE_ASYNCIO=1 python -m pytest -rsx

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

# run PEP8 check and print statistics
pep8:
	pep8 --statistics --ignore=E501 -qq autobahn

# run PEP8 check and show source for offending code
pep8show:
	pep8 --show-source --ignore=E501 autobahn

# run autopep8 to automatically transform offending code
autopep8:
	autopep8 -ri --aggressive autobahn

# This will run pep8, pyflakes and can skip lines that end with # noqa
flake8:
	flake8 --ignore=E501 autobahn

# run PyLint
pylint:
	pylint -d line-too-long,invalid-name autobahn

# on Unix, check for files with Windows line endings
find_windows_files:
	find . -name "*" -exec file {} \; | grep "CRLF"

# on Windows (Git Bash), check for files with Unix lines endings
find_unix_files:
	find . -name "*" -exec dos2unix -tv {} \; 2>&1 | grep "Unix"
