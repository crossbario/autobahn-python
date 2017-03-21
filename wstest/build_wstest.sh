#!/bin/sh

wget https://bitbucket.org/pypy/pypy/downloads/pypy2-v5.7.0-linux64.tar.bz2
mkdir -p ./wstest
tar xvf ./pypy2-v5.7.0-linux64.tar.bz2 --strip-components=1 -C ./wstest
wget https://bootstrap.pypa.io/get-pip.py
./wstest/bin/pypy get-pip.py
