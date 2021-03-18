.PHONY: downloads

CURDIR := $(CURDIR)
REPORTDATE := `date -u +"%Y-%m-%d"`

AUTOBAHN_TESTSUITE_DOCKER := crossbario/autobahn-testsuite:0.8.2@sha256:5d4ba3aa7d6ab2fdbf6606f3f4ecbe4b66f205ce1cbc176d6cdf650157e52242

default:
	@echo 'targets: clean, downloads, build_wstest'


clean:
	-rm -rf ./reports
	-rm -rf ./venv*
	-rm -rf ./wstest

dist_clean: clean
	-rm -rf ./downloads

clean_reports:
	-rm -rf ./reports

# https://s3.eu-central-1.amazonaws.com/crossbario.com/reports/autobahn-testsuite-2021-03-16/clients/index.html
# https://crossbario.com/reports/autobahn-testsuite-2021-03-16/clients/index.html
upload_reports:
	./wstest/bin/aws s3 sync \
		--delete --acl public-read --region=eu-central-1 \
		reports \
		s3://crossbario.com/reports/autobahn-testsuite-$(REPORTDATE)


downloads:
	mkdir -p downloads
	wget -P downloads https://bootstrap.pypa.io/get-pip.py
	wget -P downloads https://downloads.python.org/pypy/pypy2.7-v7.3.3-linux64.tar.bz2
	wget -P downloads https://downloads.python.org/pypy/pypy3.7-v7.3.3-linux64.tar.bz2
	wget -P downloads https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tar.xz
	wget -P downloads https://www.python.org/ftp/python/3.9.2/Python-3.9.2.tar.xz


# needs CPython 2 or PyPy 2, and https://pypi.org/project/autobahntestsuite/0.8.2/
build_wstest:
	mkdir -p ./wstest
	tar xvf ./downloads/pypy2.7-v7.3.3-linux64.tar.bz2 --strip-components=1 -C ./wstest
	./wstest/bin/pypy ./downloads/get-pip.py
	# ./wstest/bin/pip install -e ../../autobahn-testsuite/autobahntestsuite
	./wstest/bin/pip install "autobahntestsuite>=0.8.2"
	./wstest/bin/pip install awscli


build_pypy3:
	rm -rf ./pypy3
	mkdir -p ./pypy3
	tar xvf ./downloads/pypy3.7-v7.3.3-linux64.tar.bz2 --strip-components=1 -C ./pypy3
	cd ./pypy3/bin && ln -s pypy3 python && cd ../..
	./pypy3/bin/python ./downloads/get-pip.py
	./pypy3/bin/pip install virtualenv
	./pypy3/bin/python -V

build_cpy3:
	rm -rf ./cpy3_build
	mkdir -p ./cpy3_build
	tar xvf ./downloads/Python-3.9.2.tar.xz --strip-components=1 -C ./cpy3_build
	cd ./cpy3_build && ./configure --prefix=${CURDIR}/cpy3 && make && make install
	rm -rf ./cpy3_build
	./cpy3/bin/pip install virtualenv
	./cpy3/bin/python -V

build: build_wstest \
	   build_pypy3 \
	   build_cpy3


setup_pypy3_tx:
	./pypy3/bin/virtualenv ./venv_pypy3_tx
	cd .. && ./wstest/venv_pypy3_tx/bin/pip install -e .[twisted,compress]

setup_pypy3_aio:
	./pypy3/bin/virtualenv ./venv_pypy3_aio
	cd .. && ./wstest/venv_pypy3_aio/bin/pip install -e .[asyncio,compress]

setup_cpy3_tx:
	./cpy3/bin/virtualenv ./venv_cpy3_tx
	cd .. && ./wstest/venv_cpy3_tx/bin/pip install -e .[accelerate,twisted,compress]

setup_cpy3_aio:
	./cpy3/bin/virtualenv ./venv_cpy3_aio
	cd .. && ./wstest/venv_cpy3_aio/bin/pip install -e .[accelerate,asyncio,compress]

setup: setup_pypy3_tx setup_pypy3_aio setup_cpy3_tx setup_cpy3_aio


versions:
	@echo ""
	@echo "wstest (uses PyPy 2):"
	@echo ""
	./wstest/bin/pypy -V

	@echo ""
	@echo "CPython 3:"
	@echo ""
	./cpy3/bin/python -V
	@echo "Autobahn - CPython 3 / Twisted:"
	@./venv_cpy3_tx/bin/python -c "import autobahn; print('autobahn-{}'.format(autobahn.__version__))"
	@echo "Autobahn - CPython 3 / asyncio:"
	@./venv_cpy3_aio/bin/python -c "import autobahn; print('autobahn-{}'.format(autobahn.__version__))"

	@echo ""
	@echo "PyPy 3:"
	@echo ""
	./pypy3/bin/python -V
	@echo "Autobahn - PyPy 3 / Twisted:"
	@./venv_pypy3_tx/bin/python -c "import autobahn; print('autobahn-{}'.format(autobahn.__version__))"
	@echo "Autobahn - PyPy 3 / asyncio:"
	@./venv_pypy3_aio/bin/python -c "import autobahn; print('autobahn-{}'.format(autobahn.__version__))"


wstest_server_full:
	./wstest/bin/wstest -m fuzzingserver --spec=fuzzingserver-full.json

wstest_server_quick:
	./wstest/bin/wstest -m fuzzingserver --spec=fuzzingserver-quick.json


wstest_server_docker_pull:
	docker pull $(AUTOBAHN_TESTSUITE_DOCKER)

wstest_server_docker_stop:
	docker rm --force fuzzingserver

wstest_server_docker_full:
	docker run -it --rm \
		-v ${PWD}/fuzzingserver-full.json:/config/fuzzingserver.json:ro \
		-v ${PWD}/reports:/reports \
		-p 9001:9001 \
		--name autobahn \
		$(AUTOBAHN_TESTSUITE_DOCKER)

wstest_server_docker_quick:
	docker run -d --rm --name fuzzingserver \
		-u `id -u`:`id -g` \
		-v ${PWD}/fuzzingserver-quick.json:/config/fuzzingserver.json:ro \
		-v ${PWD}/reports:/reports \
		-p 9001:9001 \
		$(AUTOBAHN_TESTSUITE_DOCKER)


test_pypy3_tx_client:
	./venv_pypy3_tx/bin/python testee_client_tx.py

test_pypy3_aio_client:
	./venv_pypy3_tx/bin/python testee_client_aio.py

test_cpy3_tx_client:
	./venv_cpy3_tx/bin/python testee_client_tx.py

test_cpy3_aio_client:
	./venv_cpy3_tx/bin/python testee_client_aio.py

test_tx_clients: \
	test_pypy3_tx_client \
	test_cpy3_tx_client

test_aio_clients: \
	test_pypy3_aio_client \
	test_cpy3_aio_client

test_clients: \
	test_tx_clients \
	test_aio_clients


start_cpy3_tx_server:
	./venv_cpy3_tx/bin/python testee_server_tx.py --url ws://127.0.0.1:9011 &

start_pypy3_tx_server:
	./venv_pypy3_tx/bin/python testee_server_tx.py --url ws://127.0.0.1:9013 &

start_cpy3_aio_server:
	./venv_cpy3_aio/bin/python testee_server_aio.py --url ws://127.0.0.1:9015 &

start_pypy3_aio_server:
	./venv_pypy3_aio/bin/python testee_server_aio.py --url ws://127.0.0.1:9017 &

start_tx_servers: \
	start_cpy3_tx_server \
	start_pypy3_tx_server

start_aio_servers: \
	start_cpy3_aio_server \
	start_pypy3_aio_server

start_servers: \
	start_tx_servers \
	start_aio_servers

stop_servers:
	-pkill -f "testee_server*"


# test individual server flavor - note that this will only
# produce a single report each, and it cannot be combined into
# a single report! here is the comment from wstest.py

# allow overriding servers from command line option, providing 1 server
# this is semi-useful, as you cannot accumulate a combined report for
# multiple servers by running wstest over and over again. the generated
# report is only for the last invocation - it would require a massive
# code restructering / rewriting to change that. no time for that unfort.

test_cpy3_tx_server:
	./wstest/bin/wstest -m fuzzingclient --spec=fuzzingclient-quick.json -w ws://127.0.0.1:9011

test_pypy3_tx_server:
	./wstest/bin/wstest -m fuzzingclient --spec=fuzzingclient-quick.json -w ws://127.0.0.1:9013

test_cpy3_aio_server:
	./wstest/bin/wstest -m fuzzingclient --spec=fuzzingclient-quick.json -w ws://127.0.0.1:9015

test_pypy3_aio_server:
	./wstest/bin/wstest -m fuzzingclient --spec=fuzzingclient-quick.json -w ws://127.0.0.1:9017

test_tx_servers: \
	test_cpy3_tx_server \
	test_pypy3_tx_server

test_aio_servers: \
	test_cpy3_aio_server \
	test_pypy3_aio_server

# THIS DOES NOT WORK TO PRODUCE THE FINAL COMBINED REPORT FOR ALL SERVERS!
# see above.
#test_server: \
#	test_tx_servers \
#	test_aio_servers


test_servers:
	./wstest/bin/wstest -m fuzzingclient --spec=fuzzingclient-quick.json
