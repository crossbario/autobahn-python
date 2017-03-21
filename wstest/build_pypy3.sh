#!/bin/sh

wget https://bitbucket.org/pypy/pypy/downloads/pypy3-v5.7.0-linux64.tar.bz2
mkdir -p ./pypy3
tar xvf ./pypy3-v5.7.0-linux64.tar.bz2 --strip-components=1 -C ./pypy3
wget https://bootstrap.pypa.io/get-pip.py
cd ./pypy3/bin && ln -s pypy3 python && cd ../..
./pypy3/bin/python -V
./pypy3/bin/python get-pip.py
./pypy3/bin/pip install virtualenv
