#!/usr/bin/env python

# scripted demo for https://asciinema.org/
# to use:
# 1. create virtualenv with autobahn, ansicolors and asciinema installed:
#    pip install autobahn asciinema ansicolors
# 2. change to root of fresh AutobahnPython checkout
# 3. a) to record and upload, run:
#
#    asciinema -c ./examples/asciinema-autobahn-demo.py rec
#
# 3. b) to just test this (e.g. without recording anything):
#
#    python asciinema-autobahn-demo0.py


import os
import sys
import time
import random
import colors

prompt = 'user@machine:~/autobahn-python$ '


def interkey_interval():
    """in milliseconds"""
#    return 0  # makes testing faster
    return (random.lognormvariate(0.0, 0.5) * 30.0) / 1000.0
    return float(random.randrange(10, 50)) / 1000.0


def type_it_out(line):
    for c in line:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(interkey_interval())


def do_commands(lines):
    for line in lines:
        sys.stdout.write(colors.blue(prompt))
        type_it_out(line)
        time.sleep(0.5)
        print
        os.system(colors.strip_color(line))

commands = [
    "clear",
    colors.red('# Welcome! Here we set up and run one basic'),
    colors.red('# http://autobahn.ws example'),
    colors.red('# (Note there are many other examples to try)'),
    colors.red('#'),
    colors.red("# I presume you've got a clone of https://github.com/crossbario/autobahn-python"),
    colors.red("# in ~/autobahn-python"),
    "sleep 5",
    "clear",
    colors.red("# first, we create a virtualenv:"),
    "virtualenv venv-autobahn",
    "./venv-autobahn/bin/" + colors.bold("pip install -q --editable ."),
    colors.red("# we also need a WAMP router"),
    colors.red("# so we will use http://crossbar.io"),
    "./venv-autobahn/bin/" + colors.bold("pip install -q crossbar"),
    "clear",
    colors.red("# we have installed the AutobahnPython checkout, and crossbar."),
    colors.red("# the examples have a suitable crossbar configuration"),
    "./venv-autobahn/bin/" + colors.bold("crossbar start --cbdir examples/router/.crossbar &"),
    "sleep 2",
    colors.red('# now we run a simple "backend" which registers some callable methods'),
    "./venv-autobahn/bin/" + colors.bold("python examples/twisted/wamp/rpc/arguments/backend.py &"),
    "sleep 2",
    colors.red('# ...and a frontend that calls those methods'),
    "./venv-autobahn/bin/" + colors.bold("python examples/twisted/wamp/rpc/arguments/frontend.py"),
    colors.red('# Thanks for watching!'),
    colors.red('# http://autobahn.ws/python/wamp/examples.html'),
    "sleep 5",
]

if __name__ == '__main__':
    do_commands(commands)
