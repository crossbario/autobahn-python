default:
	@echo 'targets: clean, downloads, build_wstest'

clean:
	-rm -rf ./reports
	-rm -rf ./downloads
	-rm -rf ./venv*
	-rm -rf ./wstest

clean_reports:
	-rm -rf ./reports

downloads:
	mkdir -p downloads
	wget -P downloads https://bootstrap.pypa.io/get-pip.py
	wget -P downloads https://bitbucket.org/pypy/pypy/downloads/pypy2-v5.7.0-linux64.tar.bz2
	wget -P downloads https://bitbucket.org/pypy/pypy/downloads/pypy3-v5.7.0-linux64.tar.bz2
	wget -P downloads https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tar.xz
	wget -P downloads https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tar.xz

setup_wstest:
	mkdir -p ./wstest
	tar xvf ./downloads/pypy2-v5.7.0-linux64.tar.bz2 --strip-components=1 -C ./wstest
	./wstest/bin/pypy ./downloads/get-pip.py
	./wstest/bin/pip install autobahntestsuite

wstest_server:
	./wstest/bin/wstest -m fuzzingserver


setup_pypy2:
	mkdir -p ./pypy2
	tar xvf ./downloads/pypy2-v5.7.0-linux64.tar.bz2 --strip-components=1 -C ./pypy2
	cd ./pypy2/bin && ln -s pypy python && cd ../..
	./pypy2/bin/python ./downloads/get-pip.py
	./pypy2/bin/pip install virtualenv
	./pypy2/bin/python -V

setup_pypy3:
	mkdir -p ./pypy3
	tar xvf ./downloads/pypy3-v5.7.0-linux64.tar.bz2 --strip-components=1 -C ./pypy3
	cd ./pypy3/bin && ln -s pypy3 python && cd ../..
	./pypy3/bin/python ./downloads/get-pip.py
	./pypy3/bin/pip install virtualenv
	./pypy3/bin/python -V

setup_cpy2:
	mkdir -p ./cpy2_build
	tar xvf ./downloads/Python-2.7.13.tar.xz --strip-components=1 -C ./cpy2_build
	cd ./cpy2_build && ./configure --prefix=../cpy2 && make && make install

setup_pypy2_tx_client:
	./pypy2/bin/virtualenv ./venv_pypy2_tx_client
	./venv_pypy2_tx_client/bin/pip install -e ..[twisted]

setup_pypy2_aio_client:
	./pypy2/bin/virtualenv ./venv_pypy2_aio_client
	./venv_pypy2_aio_client/bin/pip install -e ..[asyncio]

setup_pypy3_tx_client:
	./pypy3/bin/virtualenv ./venv_pypy3_tx_client
	./venv_pypy3_tx_client/bin/pip install -e ..[twisted]

setup_pypy3_aio_client:
	./pypy3/bin/virtualenv ./venv_pypy3_aio_client
	./venv_pypy3_aio_client/bin/pip install -e ..[asyncio]


test_pypy2_tx_client:
	./venv_pypy2_tx_client/bin/python testee_client_tx.py

test_pypy2_aio_client:
	./venv_pypy2_aio_client/bin/python testee_client_aio.py

test_pypy3_tx_client:
	./venv_pypy3_tx_client/bin/python testee_client_tx.py

test_pypy3_aio_client:
	./venv_pypy3_tx_client/bin/python testee_client_aio.py


test: \
	test_pypy2_tx_client \
	test_pypy3_tx_client

broken: \
	test_pypy2_aio_client \
	test_pypy3_aio_client
