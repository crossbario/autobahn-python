CURDIR := $(CURDIR)

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

upload_reports:
	./wstest/bin/aws s3 sync reports s3://autobahn.ws/testsuite/reports \
		--delete --acl public-read --region=eu-central-1


downloads:
	mkdir -p downloads
	wget -P downloads https://bootstrap.pypa.io/get-pip.py
	wget -P downloads https://bitbucket.org/pypy/pypy/downloads/pypy2-v5.10.0-linux64.tar.bz2
	wget -P downloads https://bitbucket.org/pypy/pypy/downloads/pypy3-v5.10.1-linux64.tar.bz2
	wget -P downloads https://www.python.org/ftp/python/2.7.14/Python-2.7.14.tar.xz
	wget -P downloads https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tar.xz


build_wstest:
	mkdir -p ./wstest
	tar xvf ./downloads/pypy2-v5.10.0-linux64.tar.bz2 --strip-components=1 -C ./wstest
	./wstest/bin/pypy ./downloads/get-pip.py
	./wstest/bin/pip install autobahntestsuite
	./wstest/bin/pip install awscli


build_pypy2:
	rm -rf ./pypy2
	mkdir -p ./pypy2
	tar xvf ./downloads/pypy2-v5.10.0-linux64.tar.bz2 --strip-components=1 -C ./pypy2
	cd ./pypy2/bin && ln -s pypy python && cd ../..
	./pypy2/bin/python ./downloads/get-pip.py
	./pypy2/bin/pip install virtualenv
	./pypy2/bin/python -V

build_pypy3:
	rm -rf ./pypy3
	mkdir -p ./pypy3
	tar xvf ./downloads/pypy3-v5.10.1-linux64.tar.bz2 --strip-components=1 -C ./pypy3
	cd ./pypy3/bin && ln -s pypy3 python && cd ../..
	./pypy3/bin/python ./downloads/get-pip.py
	./pypy3/bin/pip install virtualenv
	./pypy3/bin/python -V

build_cpy2:
	rm -rf ./cpy2_build
	mkdir -p ./cpy2_build
	tar xvf ./downloads/Python-2.7.14.tar.xz --strip-components=1 -C ./cpy2_build
	cd ./cpy2_build && ./configure --prefix=${CURDIR}/cpy2 && make && make install
	rm -rf ./cpy2_build
	./cpy2/bin/python ./downloads/get-pip.py
	./cpy2/bin/pip install virtualenv
	./cpy2/bin/python -V

build_cpy3:
	rm -rf ./cpy3_build
	mkdir -p ./cpy3_build
	tar xvf ./downloads/Python-3.6.4.tar.xz --strip-components=1 -C ./cpy3_build
	cd ./cpy3_build && ./configure --prefix=${CURDIR}/cpy3 && make && make install
	cd ./cpy3/bin && ln -s python3 python && cd ../..
	cd ./cpy3/bin && ln -s pip3 pip && cd ../..
	rm -rf ./cpy3_build
	./cpy3/bin/pip install virtualenv
	./cpy3/bin/python -V

build: build_wstest \
	   build_pypy2 \
	   build_pypy3 \
	   build_cpy2 \
	   build_cpy3


versions:
	./cpy2/bin/python -V
	./cpy3/bin/python -V
	./pypy2/bin/python -V
	./pypy3/bin/python -V


setup_pypy2_tx:
	./pypy2/bin/virtualenv ./venv_pypy2_tx
	./venv_pypy2_tx/bin/pip install -e ..[twisted]

setup_pypy2_aio:
	./pypy2/bin/virtualenv ./venv_pypy2_aio
	./venv_pypy2_aio/bin/pip install -e ..[asyncio]

setup_pypy3_tx:
	./pypy3/bin/virtualenv ./venv_pypy3_tx
	./venv_pypy3_tx/bin/pip install -e ..[twisted]

setup_pypy3_aio:
	./pypy3/bin/virtualenv ./venv_pypy3_aio
	./venv_pypy3_aio/bin/pip install -e ..[asyncio]

setup_cpy2_tx:
	./cpy2/bin/virtualenv ./venv_cpy2_tx
	./venv_cpy2_tx/bin/pip install -e ..[twisted]

setup_cpy2_aio:
	./cpy2/bin/virtualenv ./venv_cpy2_aio
	./venv_cpy2_aio/bin/pip install -e ..[asyncio]

setup_cpy3_tx:
	./cpy3/bin/virtualenv ./venv_cpy3_tx
	./venv_cpy3_tx/bin/pip install -e ..[twisted]

setup_cpy3_aio:
	./cpy3/bin/virtualenv ./venv_cpy3_aio
	./venv_cpy3_aio/bin/pip install -e ..[asyncio]

setup: setup_pypy2_tx \
	   setup_pypy2_aio \
	   setup_pypy3_tx \
	   setup_pypy3_aio \
	   setup_cpy2_tx \
	   setup_cpy2_aio \
	   setup_cpy3_tx \
	   setup_cpy3_aio


wstest_server:
	./wstest/bin/wstest -m fuzzingserver


test_pypy2_tx_client:
	./venv_pypy2_tx/bin/python testee_client_tx.py

test_pypy2_aio_client:
	./venv_pypy2_aio/bin/python testee_client_aio.py

test_pypy3_tx_client:
	./venv_pypy3_tx/bin/python testee_client_tx.py

test_pypy3_aio_client:
	./venv_pypy3_tx/bin/python testee_client_aio.py

test_cpy2_tx_client:
	./venv_cpy2_tx/bin/python testee_client_tx.py

test_cpy2_aio_client:
	./venv_cpy2_aio/bin/python testee_client_aio.py

test_cpy3_tx_client:
	./venv_cpy3_tx/bin/python testee_client_tx.py

test_cpy3_aio_client:
	./venv_cpy3_tx/bin/python testee_client_aio.py


test_tx_client: \
	test_pypy2_tx_client \
	test_pypy3_tx_client \
	test_cpy2_tx_client \
	test_cpy3_tx_client

test_aio_client: \
	test_pypy2_aio_client \
	test_pypy3_aio_client \
	test_cpy2_aio_client \
	test_cpy3_aio_client

test_client: \
	test_tx_client \
	test_aio_client


start_cpy2_tx_server:
	./venv_cpy2_tx/bin/python testee_server_tx.py --url ws://127.0.0.1:9010 &

start_cpy3_tx_server:
	./venv_cpy3_tx/bin/python testee_server_tx.py --url ws://127.0.0.1:9011 &

start_pypy2_tx_server:
	./venv_pypy2_tx/bin/python testee_server_tx.py --url ws://127.0.0.1:9012 &

start_pypy3_tx_server:
	./venv_pypy3_tx/bin/python testee_server_tx.py --url ws://127.0.0.1:9013 &


start_cpy2_aio_server:
	./venv_cpy2_aio/bin/python testee_server_aio.py --url ws://127.0.0.1:9014 &

start_cpy3_aio_server:
	./venv_cpy3_aio/bin/python testee_server_aio.py --url ws://127.0.0.1:9015 &

start_pypy2_aio_server:
	./venv_pypy2_aio/bin/python testee_server_aio.py --url ws://127.0.0.1:9016 &

start_pypy3_aio_server:
	./venv_pypy3_aio/bin/python testee_server_aio.py --url ws://127.0.0.1:9017 &


start_tx_server: \
	start_cpy2_tx_server \
	start_cpy3_tx_server \
	start_pypy2_tx_server \
	start_pypy3_tx_server

start_aio_server: \
	start_cpy2_aio_server \
	start_cpy3_aio_server \
	start_pypy2_aio_server \
	start_pypy3_aio_server

start_server: \
	start_tx_server \
	start_aio_server


stop_server:
	-pkill -f "testee_server*"


# test individual server flavor - note that this will only
# produce a single report each, and it cannot be combined into
# a single report! here is the comment from wstest.py

# allow overriding servers from command line option, providing 1 server
# this is semi-useful, as you cannot accumulate a combined report for
# multiple servers by running wstest over and over again. the generated
# report is only for the last invocation - it would require a massive
# code restructering / rewriting to change that. no time for that unfort.

test_cpy2_tx_server:
	./wstest/bin/wstest -m fuzzingclient -w ws://127.0.0.1:9010

test_cpy3_tx_server:
	./wstest/bin/wstest -m fuzzingclient -w ws://127.0.0.1:9011

test_pypy2_tx_server:
	./wstest/bin/wstest -m fuzzingclient -w ws://127.0.0.1:9012

test_pypy3_tx_server:
	./wstest/bin/wstest -m fuzzingclient -w ws://127.0.0.1:9013


test_cpy2_aio_server:
	./wstest/bin/wstest -m fuzzingclient -w ws://127.0.0.1:9014

test_cpy3_aio_server:
	./wstest/bin/wstest -m fuzzingclient -w ws://127.0.0.1:9015

test_pypy2_aio_server:
	./wstest/bin/wstest -m fuzzingclient -w ws://127.0.0.1:9016

test_pypy3_aio_server:
	./wstest/bin/wstest -m fuzzingclient -w ws://127.0.0.1:9017


test_tx_server: \
	test_cpy2_tx_server \
	test_cpy3_tx_server \
	test_pypy2_tx_server \
	test_pypy3_tx_server

test_aio_server: \
	test_cpy2_aio_server \
	test_cpy3_aio_server \
	test_pypy2_aio_server \
	test_pypy3_aio_server

# THIS DOES NOT WORK TO PRODUCE THE FINAL COMBINED REPORT FOR ALL SERVERS!
# see above.
#test_server: \
#	test_tx_server \
#	test_aio_server


test_server:
	./wstest/bin/wstest -m fuzzingclient
