#!/bin/bash

docker rmi -f $(docker images -q crossbario/auobahn-python-aarch64:* | uniq)
