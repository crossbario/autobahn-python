#!/bin/bash

docker rmi -f $(docker images -q crossbario/autobahn-python-armhf:* | uniq)
