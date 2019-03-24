###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from __future__ import absolute_import

# this module is available as the 'wamp' command-line tool or as
# 'python -m autobahn'

import sys
import argparse

from autobahn.twisted.component import Component, run
from autobahn.wamp.exception import ApplicationError


## XXX how to find connection config?
# - if there's a .crossbar/ here, load .crossbar/config.{json,yaml}
#   and connect to any transport ('--transport-id X' on the cli?)
# - cli options
# - read a config.json from stdin, make all transports available by name/id?

# wamp [options] {call,publish,subscribe,register} wamp-uri args --keywords kwargs
# all kwargs are "some-arg=thevalue" following a --keywords


top = argparse.ArgumentParser(prog="wamp")
top.add_argument(
    '--url',
    action='store',
    help='A WAMP URL to connect to, like ws://127.0.0.1:8080/ws or rs://localhost:1234/',
    required=True,
)
top.add_argument(
    '--realm', '-r',
    action='store',
    help='The realm to join',
    default='default',
)
sub = top.add_subparsers(
    title="subcommands",
    dest="subcommand_name",
#    help="ohai what goes here?",
)

call = sub.add_parser(
    'call',
    help='Do a WAMP call() and print any results',
)
call.add_argument(
    'uri',
    type=str,
    help="A WAMP URI to call"
)
call.add_argument(
    'call_args',
    nargs='*',
    help="All additional arguments are positional args (HOWTO do kwargs?)",
)
# XXX FIXME: can do like "wamp call pos0 pos1 --kw name value --kw name value pos2"


def _create_component(options):
    if options.url.startswith('ws://'):
        kind = 'websocket'
    elif options.url.startswith('rs://'):
        kind = 'rawsocket'
    else:
        raise ValueError(
            "URL should start with ws:// or rs://"
        )
    return Component(
        transports=[{
            "type": kind,
            "url": options.url,
        }],
        authentication={
            "cryptosign": {
                "authid": "wheel_pusher",
                "authrole": "wheel_pusher",
                "privkey": "4778956c24819ac2765fbe2e7d38b798f59d0d96931d519d70c36b5889e43a7e",
            }
        },
        realm=options.realm,
    )


def _main():
    options = top.parse_args()
    component = _create_component(options)

    if options.subcommand_name is None:
        print("Must select a subcommand")
        sys.exit(1)

    exit_code = [0]

    if options.subcommand_name == 'call':
        call_args = list(options.call_args)
        call_kwargs = dict()

        @component.on_join
        async def _(session, details):
            print(f"connected: authrole={details.authrole}")
            try:
                results = await session.call(options.uri, *call_args, **call_kwargs)
                print("result: {}".format(results))
            except ApplicationError as e:
                print("\n{}: {}\n".format(e.error, ''.join(e.args)))
                exit_code[0] = 5
            await session.leave()

    run([component])
    print("hi")
    sys.exit(exit_code[0])


if __name__ == "__main__":
    _main()
