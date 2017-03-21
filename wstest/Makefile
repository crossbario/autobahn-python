fuzzingserver:
	./wstest/bin/wstest -m fuzzingserver

clean:
	-rm -rf ./reports
	-rm -rf ./downloads
	-rm -rf ./venv

download:
	mkdir -p downloads
	cd downloads
	wget -P downloads https://bootstrap.pypa.io/get-pip.py
	wget -P downloads https://bitbucket.org/pypy/pypy/downloads/pypy2-v5.7.0-linux64.tar.bz2
	wget -P downloads https://bitbucket.org/pypy/pypy/downloads/pypy3-v5.7.0-linux64.tar.bz2
	wget -P downloads https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tar.xz

build_wstest:
	-rm -rf ./wstest
	mkdir -p ./wstest
	tar xvf ./pypy2-v5.7.0-linux64.tar.bz2 --strip-components=1 -C ./wstest
	./wstest/bin/pypy get-pip.py



# CPython 2

# PyPy 2

setup_client_pypy2_tx:
	./pypy2-v5.7.0-linux64/bin/virtualenv ./venv_client_pypy2_tx
	./venv_client_pypy2_tx/bin/pip install -e ..[twisted]

setup_client_pypy2_aio:
	./pypy2-v5.7.0-linux64/bin/virtualenv ./venv_client_pypy2_aio
	./venv_client_pypy2_aio/bin/pip install -e ..[asyncio]

# PyPy 3

setup_client_pypy3_tx:
	./pypy3/bin/virtualenv ./venv_client_pypy3_tx
	./venv_client_pypy3_tx/bin/pip install -e ..[twisted]

setup_client_pypy3_aio:
	./pypy3/bin/virtualenv ./venv_client_pypy3_aio
	./venv_client_pypy3_aio/bin/pip install -e ..[asyncio]


# ALL

setup: setup_client_pypy3_tx setup_client_pypy3_aio




test_client_pypy3_tx:
	./venv_client_pypy3_tx/bin/python testee_client_tx.py

test_client_pypy3_aio:
	./venv_client_pypy3_aio/bin/python testee_client_aio.py


test_client_pypy2_tx:
	./venv_client_pypy2_twisted/bin/python testee_client_tx.py

test_client_pypy2_aio:
	./venv_client_pypy2_aio/bin/python testee_client_aio.py



test: \
	test_client_pypy2_tx \
	test_client_pypy3_tx

broken: \
	test_client_pypy2_aio \
	test_client_pypy3_aio
