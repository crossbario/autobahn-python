.PHONY: test docs pep8 build

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
	-pip uninstall -y pytest_asyncio # remove the broken shit
	-pip uninstall -y pytest_cov # remove the broken shit
	# enforce use of bundled libsodium
	-pip install --force-reinstall git+https://github.com/crossbario/py-eth-sig-utils.git@master#egg=py-eth-sig-utils
	AUTOBAHN_USE_NVX=1 SODIUM_INSTALL=bundled pip install -e .[all]

build:
	-rm -f dist/*
	# python setup.py sdist bdist_wheel --universal
	AUTOBAHN_USE_NVX=1 python setup.py sdist bdist_wheel
	ls -la dist

# upload to our internal deployment system
upload: clean
	python setup.py sdist bdist_wheel --universal
	aws s3 cp --acl public-read \
		dist/autobahn-*.whl \
		s3://fabric-deploy/autobahn/

# cleanup everything
clean:
	-rm -f ./*.so
	-rm -rf ./docs/build
	-rm -rf ./.cache
	-rm -rf ./autobahn.egg-info
	-rm -rf ./build
	-rm -rf ./dist
	-rm -rf ./temp
	-rm -rf ./_trial_temp
	-rm -rf ./.tox
	-rm -rf ./.eggs
	-rm -rf ./htmlcov
	-rm -f ./.coverage
	-rm -f ./coverage.xml
	-rm -f ./.coverage.*
	-rm -rf ~/coverage
	-rm -f  ./twisted/plugins/dropin.cache
	-find . -name "*dropin.cache.new" -type f -exec rm -f {} \;
	-find . -name "*.tar.gz" -type f -exec rm -f {} \;
	-find . -name "*.egg" -type f -exec rm -f {} \;
	-find . -name "*.pyc" -type f -exec rm -f {} \;

	# Learn to love the shell! http://unix.stackexchange.com/a/115869/52500
	-find . \( -name "*__pycache__" -type d \) -prune -exec rm -rf {} +

# publish to PyPI
publish: clean
	python setup.py sdist bdist_wheel --universal
	twine upload dist/*

docs:
	cd docs && make html

spelling:
	cd docs && sphinx-build -b spelling . _spelling


test_nvx:
	python -m pytest -rsx autobahn/nvx/test
	USE_TWISTED=1 trial autobahn.nvx.test.test_utf8validator

test_styleguide:
	flake8 --statistics --max-line-length=119 -qq autobahn

# direct test via pytest (only here because of setuptools test integration)
test_pytest:
	python -m pytest -rsx autobahn/

# test via setuptools command
test_setuptools:
	python setup.py test

test:
	tox -e flake8,py37-twtrunk,py37-asyncio,coverage

#test: flake8 test_twisted test_asyncio

# test under Twisted
test_twisted:
	USE_TWISTED=1 trial autobahn
	#WAMP_ROUTER_URL="ws://127.0.0.1:8080/ws" USE_TWISTED=1 trial autobahn

test_rng:
	USE_TWISTED=1 trial autobahn.test.test_rng

test_tx_serializer:
	USE_TWISTED=1 trial autobahn.wamp.test.test_serializer

test_tx_cryptobox:
	USE_TWISTED=1 trial autobahn.wamp.test.test_cryptobox

test_tx_choosereactor:
	USE_TWISTED=1 trial autobahn.twisted.test.test_choosereactor

test_twisted_coverage:
	-rm .coverage
	USE_TWISTED=1 coverage run --omit=*/test/* --source=autobahn `which trial` autobahn
#	coverage -a -d annotated_coverage
	coverage html
	coverage report --show-missing

test_coverage:
	-rm .coverage
	tox -e py27-twtrunk,py27-asyncio,py36-asyncio
	coverage combine
	coverage html
	coverage report --show-missing

# test under asyncio
test_asyncio:
	USE_ASYNCIO=1 python -m pytest -rsx autobahn
	#WAMP_ROUTER_URL="ws://127.0.0.1:8080/ws" USE_ASYNCIO=1 python -m pytest -rsx

test_cs1:
	USE_ASYNCIO=1 python -m pytest -s -v autobahn/wamp/test/test_cryptosign.py

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
	flake8 --ignore=E402,E501,E722,E741,N801,N802,N803,N805,N806,N815 \
	    --exclude "autobahn/wamp/message_fbs.py,autobahn/wamp/gen/*"\
	    autobahn

# run PyLint
pylint:
	pylint -d line-too-long,invalid-name autobahn

# on Unix, check for files with Windows line endings
find_windows_files:
	find . -name "*" -exec file {} \; | grep "CRLF"

# on Windows (Git Bash), check for files with Unix lines endings
find_unix_files:
	find . -name "*" -exec dos2unix -tv {} \; 2>&1 | grep "Unix"

# sudo apt install gource ffmpeg
gource:
	gource \
	--path . \
	--seconds-per-day 0.15 \
	--title "autobahn-python" \
	-1280x720 \
	--file-idle-time 0 \
	--auto-skip-seconds 0.75 \
	--multi-sampling \
	--stop-at-end \
	--highlight-users \
	--hide filenames,mouse,progress \
	--max-files 0 \
	--background-colour 000000 \
	--disable-bloom \
	--font-size 24 \
	--output-ppm-stream - \
	--output-framerate 30 \
	-o - \
	| ffmpeg \
	-y \
	-r 60 \
	-f image2pipe \
	-vcodec ppm \
	-i - \
	-vcodec libx264 \
	-preset ultrafast \
	-pix_fmt yuv420p \
	-crf 1 \
	-threads 0 \
	-bf 0 \
	autobahn-python.mp4

#
# generate (a special set of) WAMP message classes from FlatBuffers schema
#

# input .fbs files for schema
FBSFILES=./autobahn/wamp/flatbuffers/*.fbs

# flatc compiler to use
FLATC=flatc

clean_fbs:
	-rm -rf ./autobahn/wamp/gen/

build_fbs:
	# generate schema type library (*.bfbs files)
	$(FLATC) -o ./autobahn/wamp/gen/schema/ --binary --schema --bfbs-comments --bfbs-builtins $(FBSFILES)
	@find ./autobahn/wamp/gen/schema/ -name "*.bfbs" | wc -l

	# generate schema Python bindings (*.py files)
	$(FLATC) -o ./autobahn/wamp/gen/ --python $(FBSFILES)
	@find ./autobahn/wamp/gen/ -name "*.py" | wc -l

	# generate schema C++ bindings (*.cpp/hpp files)
	# $(FLATC) -o /tmp/gen/ --cpp $(FBSFILES)
	# @find /tmp/gen/
