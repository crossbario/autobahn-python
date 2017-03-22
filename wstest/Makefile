CURDIR := $(CURDIR)

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


build_wstest:
	mkdir -p ./wstest
	tar xvf ./downloads/pypy2-v5.7.0-linux64.tar.bz2 --strip-components=1 -C ./wstest
	./wstest/bin/pypy ./downloads/get-pip.py
	./wstest/bin/pip install autobahntestsuite


build_pypy2:
	mkdir -p ./pypy2
	tar xvf ./downloads/pypy2-v5.7.0-linux64.tar.bz2 --strip-components=1 -C ./pypy2
	cd ./pypy2/bin && ln -s pypy python && cd ../..
	./pypy2/bin/python ./downloads/get-pip.py
	./pypy2/bin/pip install virtualenv
	./pypy2/bin/python -V

build_pypy3:
	mkdir -p ./pypy3
	tar xvf ./downloads/pypy3-v5.7.0-linux64.tar.bz2 --strip-components=1 -C ./pypy3
	cd ./pypy3/bin && ln -s pypy3 python && cd ../..
	./pypy3/bin/python ./downloads/get-pip.py
	./pypy3/bin/pip install virtualenv
	./pypy3/bin/python -V

build_cpy2:
	mkdir -p ./cpy2_build
	tar xvf ./downloads/Python-2.7.13.tar.xz --strip-components=1 -C ./cpy2_build
	cd ./cpy2_build && ./configure --prefix=${CURDIR}/cpy2 && make && make install
	rm -rf ./cpy2_build
	./cpy2/bin/python ./downloads/get-pip.py
	./cpy2/bin/pip install virtualenv
	./cpy2/bin/python -V

build_cpy3:
	mkdir -p ./cpy3_build
	tar xvf ./downloads/Python-3.6.0.tar.xz --strip-components=1 -C ./cpy3_build
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
