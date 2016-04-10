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
	# enforce use of bundled libsodium
	export SODIUM_INSTALL=bundled
	pip install --upgrade -e .[all,dev]

# cleanup everything
clean:
	rm -rf ./.cache
	rm -rf ./autobahn.egg-info
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./temp
	rm -rf ./_trial_temp
	rm -rf ./.tox
	rm -rf ./.eggs
	rm -f  ./twisted/plugins/dropin.cache
	find . -name "*dropin.cache.new" -type f -exec rm -f {} \;
	find . -name "*.tar.gz" -type f -exec rm -f {} \;
	find . -name "*.egg" -type f -exec rm -f {} \;
	find . -name "*.pyc" -type f -exec rm -f {} \;

	# Learn to love the shell! http://unix.stackexchange.com/a/115869/52500
	find . \( -name "*__pycache__" -type d \) -prune -exec rm -rf {} +

# publish to PyPI
publish: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

test_styleguide:
	flake8 --statistics --max-line-length=119 -qq autobahn

# direct test via pytest (only here because of setuptools test integration)
test_pytest:
	python -m pytest -rsx autobahn/

# test via setuptools command
test_setuptools:
	python setup.py test

test: flake8 test_twisted test_asyncio

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

test_coverage:
	-rm .coverage
	tox -e py27-twcurrent,py27-trollius,py34-asyncio
	coverage combine
	coverage html
	coverage report --show-missing

# test under asyncio
test_asyncio:
	USE_ASYNCIO=1 python -m pytest -rsx autobahn
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
	flake8 --ignore=E402,E501,N801,N802,N803,N805,N806 autobahn

# run PyLint
pylint:
	pylint -d line-too-long,invalid-name autobahn

# on Unix, check for files with Windows line endings
find_windows_files:
	find . -name "*" -exec file {} \; | grep "CRLF"

# on Windows (Git Bash), check for files with Unix lines endings
find_unix_files:
	find . -name "*" -exec dos2unix -tv {} \; 2>&1 | grep "Unix"

find_tavendo:
	find . -path ./.git -prune -o -type f -exec grep -Hi "tavendo" {} \; | grep -v "Copyright (c) Tavendo"
