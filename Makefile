.PHONY: test docs pep8 build

WHEELS=https://crossbarbuilder.s3.eu-central-1.amazonaws.com/wheels
XBRNETWORK=${HOME}/.local/bin/xbrnetwork

all:
	@echo "Targets:"
	@echo ""
	@echo "   clean            Cleanup"
	@echo "   install          Local install"
	@echo "   publish          Clean build, register and publish to PyPi"
	@echo "   test             Run unit tests"
	@echo "   flake8           Run flake8 code checking"
	@echo ""

# deprecated with v21.2.1 (ABI files are no longer bundled in this package)
abi_files:
	curl -s https://xbr.network/lib/abi/xbr-protocol-latest.zip -o /tmp/xbr-protocol-latest.zip
	unzip -t /tmp/xbr-protocol-latest.zip
	rm -rf ${PWD}/autobahn/xbr/contracts
	unzip /tmp/xbr-protocol-latest.zip -d ${PWD}/autobahn/xbr/contracts

# install locally
install:
	-pip uninstall -y pytest_asyncio # remove the broken shit
	-pip uninstall -y pytest_cov # remove the broken shit
	# enforce use of bundled libsodium
	AUTOBAHN_USE_NVX=1 SODIUM_INSTALL=bundled pip install -e .[all]

build:
	-rm -f dist/*
	# AUTOBAHN_USE_NVX=0 python -m build
	AUTOBAHN_USE_NVX=1 python -m build
	ls -la dist

# upload to our internal deployment system
upload: clean
	AUTOBAHN_USE_NVX=0 python -m build
	aws s3 cp --acl public-read \
		dist/autobahn-*.whl \
		s3://fabric-deploy/autobahn/

# cleanup everything
clean: clean_docs clean_catalog
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
	-rm -f  ./twisted/plugins/dropin.cache
	-find . -name "*dropin.cache.new" -type f -exec rm -f {} \;
	-find . -name ".pytest_cache" -type d -exec rm -rf {} \;
	-find . -name "*.tar.gz" -type f -exec rm -f {} \;
	-find . -name "*.egg" -type f -exec rm -f {} \;
	-find . -name "*.pyc" -type f -exec rm -f {} \;

	# Learn to love the shell! http://unix.stackexchange.com/a/115869/52500
	-find . \( -name "*__pycache__" -type d \) -prune -exec rm -rf {} +

clean_catalog:
	cd ./autobahn/xbr/test/catalog && make clean

rebuild_catalog:
	cd ./autobahn/xbr/test/catalog && make distclean && make build

# publish to PyPI
publish: clean
	AUTOBAHN_USE_NVX=0 python -m build
	twine upload dist/*

# Prettier: Markdown docs => opinionated, auto-formatting tool that "just works"
# 	https://prettier.io/
# Config: ./.prettierrc.json
# Installation: npm install --save-dev --save-exact prettier
#
autoformat_markdown_docs:
	npx prettier --write CLAUDE.md

# rstfmt: ReST docs => opinionated, auto-formatting tool that "just works"
# 	https://github.com/dzhu/rstfmt
# Config: ./pyproject.toml
# Installation: pip install rstfmt
#
autoformat_rest_docs:
	rstfmt AI_POLICY.rst

# copy AI Policy and GitHub template files; and adjust them; in one go
copy_aipolicy_gh_tmpl:
	@python3 sync_templates.py

clean_docs:
	-rm -rf ./docs/_build
	-rm -rf ./docs/autoapi/

docs:
	tox -e sphinx

spelling:
	cd docs && sphinx-build -b spelling . _spelling

run_docs:
	twistd --nodaemon web --port=tcp:8090 --path=./docs/_build/


clean_wheels:
	rm -rf ./.wheels
	mkdir -p ./.wheels/

download_wheels:
	mkdir -p ./.wheels/
	rm -f ./.wheels/*.whl
	curl -o ./.wheels/txaio-latest-py2.py3-none-any.whl 	$(WHEELS)/txaio-latest-py2.py3-none-any.whl
	curl -o ./.wheels/zlmdb-latest-py2.py3-none-any.whl 	$(WHEELS)/zlmdb-latest-py2.py3-none-any.whl
	curl -o ./.wheels/xbr-latest-py2.py3-none-any.whl 		$(WHEELS)/xbr-latest-py2.py3-none-any.whl
	curl -o ./.wheels/autobahn-latest-py2.py3-none-any.whl 	$(WHEELS)/autobahn-latest-py2.py3-none-any.whl
	ls -la ./.wheels

build_this_wheel:
	mkdir -p ./.wheels/
	rm -f ./.wheels/autobahn*.whl
	pip3 wheel --no-deps --wheel-dir=./.wheels .
	mv .wheels/autobahn*.whl .wheels/autobahn-latest-py2.py3-none-any.whl
	ls -la ./.wheels

download_exe:
	curl -o $(XBRNETWORK) \
		https://download.crossbario.com/xbrnetwork/linux-amd64/xbrnetwork-latest
	chmod +x $(XBRNETWORK)
	$(XBRNETWORK) version

build_exe:
	tox -e buildexe

upload_exe:
	aws s3 cp --acl public-read \
		./dist/xbrnetwork \
		s3://download.crossbario.com/xbrnetwork/linux-amd64/${XBRNETWORK_EXE_FILENAME}
	aws s3 cp --acl public-read \
		./dist/xbrnetwork \
		s3://download.crossbario.com/xbrnetwork/linux-amd64/xbrnetwork-latest
	# aws s3api copy-object --acl public-read --copy-source \
	# 	download.crossbario.com/xbrnetwork/linux-amd64/${XBRNETWORK_EXE_FILENAME} \
	# 	--bucket download.crossbario.com \
	# 	--key xbrnetwork/linux-amd64/xbrnetwork-latest
	aws cloudfront create-invalidation \
		--distribution-id E2QIG9LNGCJSP9 --paths "/xbrnetwork/linux-amd64/*"

mypy:
	mypy --install-types --non-interactive autobahn

# WEB3_INFURA_PROJECT_ID must be defined for this
test_infura:
	time -f "%e" python -c "from web3.auto.infura import w3; print(w3.isConnected())"

test_xbr:
	USE_TWISTED=1 trial autobahn.xbr

test_xbr_cli:
	xbrnetwork
	xbrnetwork version
	xbrnetwork get-member
	xbrnetwork get-market --market=1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3
	xbrnetwork get-actor
	xbrnetwork get-actor --market=1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3

test_wamp_serializer:
	-USE_TWISTED=1 trial autobahn.wamp.test.test_wamp_serializer
	-USE_ASYNCIO=1 pytest autobahn/wamp/test/test_wamp_serializer.py

test_xbr_schema:
	USE_TWISTED=1 trial autobahn.xbr.test.schema
	USE_ASYNCIO=1 pytest autobahn/xbr/test/schema

test_mnemonic:
	# python -m pytest -rsx autobahn/xbr/test/test_mnemonic.py
	USE_TWISTED=1 trial autobahn.xbr.test

test_nvx:
	python -m pytest -rsx autobahn/nvx/test
	USE_TWISTED=1 trial autobahn.nvx.test.test_utf8validator

test_styleguide:
	flake8 --statistics --max-line-length=119 -qq autobahn

# direct test via pytest (only here because of setuptools test integration)
test_pytest:
	USE_ASYNCIO=1 python -m pytest -c setup.cfg -rsvx autobahn/

test:
	tox -e flake8,py37-twtrunk,py37-asyncio

#test: flake8 test_twisted test_asyncio

# test under Twisted
test_twisted:
	USE_TWISTED=1 trial autobahn
#	WAMP_ROUTER_URL="ws://127.0.0.1:8080/ws" USE_TWISTED=1 trial autobahn

test_application_runner:
	USE_TWISTED=1 trial autobahn.twisted.test.test_tx_application_runner

test_util:
	USE_TWISTED=1 trial autobahn.test.test_util

test_rng:
	USE_TWISTED=1 trial autobahn.test.test_rng

test_serializer:
	USE_TWISTED=1 trial autobahn.wamp.test.test_wamp_serializer

test_wamp_identifiers:
	USE_TWISTED=1 trial autobahn.wamp.test.test_wamp_identifiers

test_tx_cryptobox:
	USE_TWISTED=1 trial autobahn.wamp.test.test_cryptobox

test_tx_choosereactor:
	USE_TWISTED=1 trial autobahn.twisted.test.test_choosereactor

test_cryptosign:
#	USE_ASYNCIO=1 trial autobahn.wamp.test.test_wamp_cryptosign
	USE_ASYNCIO=1 pytest -s -v -rfA --ignore=./autobahn/twisted autobahn/wamp/test/test_wamp_cryptosign.py
	USE_TWISTED=1 trial autobahn.wamp.test.test_wamp_cryptosign

test_xbr_web3:
#	pytest -s -v -rfA autobahn/xbr/test/test_xbr_web3.py
	trial autobahn/xbr/test/test_xbr_web3.py

test_xbr_frealm:
#	pytest -s -v -rfA autobahn/xbr/test/test_xbr_frealm.py
	trial autobahn/xbr/test/test_xbr_frealm.py

test_wamp_scram:
	USE_ASYNCIO=1 trial autobahn.wamp.test.test_wamp_scram
	USE_TWISTED=1 trial autobahn.wamp.test.test_wamp_scram

test_xbr_argon2:
	USE_ASYNCIO=1 trial autobahn.xbr.test.test_xbr_argon2
	USE_TWISTED=1 trial autobahn.xbr.test.test_xbr_argon2

test_xbr_config:
	USE_TWISTED=1 trial autobahn.xbr.test.test_xbr_config

test_transport_details:
	USE_ASYNCIO=1 trial autobahn.wamp.test.test_wamp_transport_details
	USE_TWISTED=1 trial autobahn.wamp.test.test_wamp_transport_details

test_session_details:
	USE_ASYNCIO=1 trial autobahn.wamp.test.test_wamp_session_details
	USE_TWISTED=1 trial autobahn.wamp.test.test_wamp_session_details

test_tx_protocol:
	USE_TWISTED=1 trial autobahn.twisted.test.test_tx_protocol

test_asyncio:
	USE_ASYNCIO=1 pytest -s -v -rfP --ignore=./autobahn/twisted autobahn
#	USE_ASYNCIO=1 pytest -s -v -rA --ignore=./autobahn/twisted ./autobahn/asyncio/test/test_aio_websocket.py
#	USE_ASYNCIO=1 pytest -s -v -rA --log-cli-level=info --ignore=./autobahn/twisted ./autobahn/asyncio/test/test_aio_websocket.py

test_cs1:
	USE_ASYNCIO=1 python -m pytest -s -v autobahn/wamp/test/test_cryptosign.py

test1:
	USE_TWISTED=1 trial autobahn.wamp.test.test_wamp_uri_pattern
#	USE_TWISTED=1 trial autobahn.wamp.test.test_auth
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
	tox -c tox.ini -e flake8

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

# To build flatc from sourcces:
#
#  git clone https://github.com/google/flatbuffers.git
#  cd flatbuffers
#  git checkout v22.12.06
#  cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release
#  make
#  sudo cp ./flatc /usr/local/bin/flatc

# input .fbs files for schema
FBSFILES=./autobahn/wamp/flatbuffers/*.fbs

# flatc compiler to use
FLATC=flatc

clean_fbs:
	-rm -rf ./autobahn/wamp/gen/

build_fbs:
	# generate schema binary type library (*.bfbs files)
	$(FLATC) -o ./autobahn/wamp/gen/schema/ --binary --schema --bfbs-comments --bfbs-builtins $(FBSFILES)
	@find ./autobahn/wamp/gen/schema/ -name "*.bfbs" | wc -l

	# generate schema Python bindings (*.py files)
	$(FLATC) -o ./autobahn/wamp/gen/ --python $(FBSFILES)
	@touch ./autobahn/wamp/gen/__init__.py
	@find ./autobahn/wamp/gen/ -name "*.py" | wc -l

build_fbs_cpp:
	# generate schema C++ bindings (*.cpp/hpp files)
	$(FLATC) -o /tmp/gen-cpp/ --cpp $(FBSFILES)
	@find /tmp/gen-cpp/

build_fbs_rust:
	# generate schema Rust bindings (*.rs files)
	$(FLATC) -o /tmp/gen-rust/ --rust $(FBSFILES)
	@find /tmp/gen-rust/

fix_copyright:
	find . -type f -exec sed -i 's/Copyright (c) Crossbar.io Technologies GmbH/Copyright (c) typedef int GmbH/g' {} \;
