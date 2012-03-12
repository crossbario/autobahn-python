#!/bin/sh

rm -rf ./build
rm -rf ./autobahn.egg-info
rm -rf ./dist
find . -name "*.pyc" -exec rm {} \;
