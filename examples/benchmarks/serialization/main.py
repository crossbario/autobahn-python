###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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

"""
WAMP Message Serialization Benchmarks

Benchmarks serialization/deserialization performance of WAMP messages across
different serializers (json, msgpack, cbor, ubjson, flatbuffers) on both
CPython and PyPy.

Usage:
    # Run benchmark
    python main.py run --serializer cbor --payload_mode normal --payload_size small \\
        --profile build/profile.dat --results build

    # Generate HTML report
    python main.py index --output build
"""

import argparse
import json
import os
import platform
import random
import sys
import time
from timeit import Timer
from typing import Any, Dict, List, Optional

import humanize
import jinja2
import txaio
import vmprof

# Initialize txaio framework BEFORE importing autobahn (required for serializers)
txaio.use_asyncio()

from autobahn import util
from autobahn.wamp.message import Event, Publish
from autobahn.wamp.serializer import create_transport_serializer

from loader import (
    PAYLOAD_MODE_NORMAL,
    PAYLOAD_MODE_TRANSPARENT,
    VehicleEvent,
    load,
)

__all__ = ['main_run', 'main_index']


def main_run(args: argparse.Namespace) -> None:
    """
    Run serialization benchmark.

    Args:
        args: Parsed command-line arguments
    """
    iterations = args.iterations
    payload_mode = args.payload_mode
    payload_size = args.payload_size

    python = 'cpy' if platform.python_implementation() == 'CPython' else 'pypy'

    filename_profile = args.profile

    # Detect actual serializer implementation (e.g., ujson vs json, cbor2 vs cbor)
    if args.serializer == 'json' and 'AUTOBAHN_USE_UJSON' in os.environ:
        _serializer = 'ujson'
    elif args.serializer == 'cbor' and 'AUTOBAHN_USE_CBOR2' in os.environ:
        _serializer = 'cbor2'
    else:
        _serializer = args.serializer

    filename_results = os.path.join(
        args.results,
        f'results_{python}_{_serializer}_{payload_mode}_{payload_size}.json'
    )

    # Create serializer factory
    ser = create_transport_serializer(args.serializer)

    print('Preparing benchmarking sample data ..')
    sample, vehicles = load(payload_mode=payload_mode, payload_size=payload_size)

    # Prepare sample for display
    if isinstance(sample, bytes):
        sample_display: Any = len(sample)
    elif isinstance(sample, VehicleEvent):
        sample_dict = sample.marshal()
        if sample_dict and 'frame' in sample_dict:
            sample_dict['frame'] = f'<<<<<<<<< BINARY data, {len(sample_dict["frame"])} bytes >>>>>>>>>>'
        sample_display = sample_dict
    else:
        raise RuntimeError(f'unexpected type {type(sample)}')

    total_events = sum(len(events) for events in vehicles.values())

    print(f'Ok, data loaded from {len(vehicles)} vehicles, {total_events} events in total.')
    print(f'Sample:\n{sample_display}')
    print(f'Message serialization test starting with {ser.SERIALIZER_ID}-serializer ..')

    def loop(results: Optional[Dict[str, Any]] = None) -> None:
        """Inner benchmark loop."""
        total_bytes = 0
        total_cnt = 0

        started = time.perf_counter()

        for vehicle_id, events in vehicles.items():
            for topic, event in events:
                msg = None
                kind = random.randint(0, 1)

                if kind == 0:
                    # Create fake WAMP PUBLISH message
                    request = util.id()
                    if payload_mode == PAYLOAD_MODE_NORMAL:
                        msg = Publish(request, topic, args=[event])
                    elif payload_mode == PAYLOAD_MODE_TRANSPARENT:
                        msg = Publish(request, topic, payload=event)
                elif kind == 1:
                    # Create fake WAMP EVENT message
                    subscription = util.id()
                    publication = util.id()
                    if payload_mode == PAYLOAD_MODE_NORMAL:
                        msg = Event(subscription, publication, args=[event])
                    elif payload_mode == PAYLOAD_MODE_TRANSPARENT:
                        msg = Event(subscription, publication, payload=event)

                # Serialize WAMP message to bytes
                bytes_data, is_binary = ser.serialize(msg)

                total_bytes += len(bytes_data)
                total_cnt += 1

        secs = time.perf_counter() - started
        msg_per_sec = int(round(float(total_cnt) / secs, 0))
        bytes_per_sec = int(round(float(total_bytes) / secs, 0))

        print(
            f'Serialized {total_cnt} messages, {total_bytes} bytes in total, '
            f'{total_bytes // total_cnt} bytes/msg, {msg_per_sec} msgs/sec, '
            f'{bytes_per_sec} bytes/sec'
        )

        if results is not None:
            results['msg_bytes'] = int(round(total_bytes / total_cnt))
            if 'msgs_per_sec' not in results:
                results['msgs_per_sec'] = []
            results['msgs_per_sec'].append(msg_per_sec)
            if 'bytes_per_sec' not in results:
                results['bytes_per_sec'] = []
            results['bytes_per_sec'].append(bytes_per_sec)

    # Warm-up phase
    print(f'Warming up {ser.SERIALIZER_ID}-serializer for {iterations} iterations ..')
    t = Timer(lambda: loop())
    t.timeit(number=iterations)

    # Measurement phase with profiling
    print(f'Measuring {ser.SERIALIZER_ID}-serializer {iterations} iterations ..')
    results: Dict[str, Any] = {}
    fd = os.open(filename_profile, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o644)

    vmprof.enable(fd, period=0.01)
    t = Timer(lambda: loop(results))
    t.timeit(number=iterations)
    vmprof.disable()

    os.close(fd)

    # Calculate averages
    msgs_per_sec = int(round(sum(results['msgs_per_sec']) / len(results['msgs_per_sec'])))
    bytes_per_sec = int(round(sum(results['bytes_per_sec']) / len(results['bytes_per_sec'])))

    # Save results
    with open(filename_results, 'w') as f:
        obj = {
            'python_version': sys.version,
            'python': python,
            'events': total_events,
            'sample': sample_display,
            'iterations': iterations,
            'msg_bytes': results['msg_bytes'],
            'msgs_per_sec': msgs_per_sec,
            'bytes_per_sec': bytes_per_sec,
        }
        json.dump(obj, f)

    print(f'Done: {msgs_per_sec} msgs/sec, {bytes_per_sec} bytes/sec')


def main_index(args: argparse.Namespace) -> None:
    """
    Generate HTML report index from benchmark results.

    Args:
        args: Parsed command-line arguments
    """
    output = args.output

    templates = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        keep_trailing_newline=True,
        autoescape=True
    )

    template_index = templates.get_template('index.html')
    template_flamegraph = templates.get_template('flamegraph.html')

    report_data: Dict[str, Any] = {
        'generated': util.utcnow(),
        'results': {
            'cpy': {},
            'pypy': {},
        }
    }

    # All serializers and configurations
    serializers = ['json', 'ujson', 'msgpack', 'cbor', 'cbor2', 'ubjson', 'flatbuffers']
    payload_modes = ['normal', 'transparent']
    payload_sizes = ['empty', 'small', 'medium', 'large', 'xl', 'xxl']

    for _python in report_data['results']:
        for _ser in serializers:
            if _ser not in report_data['results'][_python]:
                report_data['results'][_python][_ser] = {}
            for _payload_mode in payload_modes:
                if _payload_mode not in report_data['results'][_python][_ser]:
                    report_data['results'][_python][_ser][_payload_mode] = {}
                for _payload_size in payload_sizes:
                    fn = os.path.join(
                        output,
                        f'results_{_python}_{_ser}_{_payload_mode}_{_payload_size}.json'
                    )
                    if os.path.isfile(fn):
                        with open(fn) as f:
                            data = json.load(f)
                            report_data['results'][_python][_ser][_payload_mode][_payload_size] = data
                        print(f'File added    : {fn}')

                        # Generate flamegraph HTML
                        fn_svg = os.path.join(
                            output,
                            f'vmprof_{_python}_{_ser}_{_payload_mode}_{_payload_size}.html'
                        )
                        with open(fn_svg, 'w') as f:
                            data['python'] = _python
                            data['serializer'] = _ser
                            data['payload_mode'] = _payload_mode
                            data['payload_size'] = _payload_size
                            s = template_flamegraph.render(
                                naturalsize=humanize.naturalsize,
                                intword=humanize.intword,
                                intcomma=humanize.intcomma,
                                sorted=sorted,
                                **data
                            )
                            f.write(s)
                    else:
                        print(f'File not found: {fn}')

                # Clean up empty configurations
                if not report_data['results'][_python][_ser][_payload_mode]:
                    del report_data['results'][_python][_ser][_payload_mode]
            if not report_data['results'][_python][_ser]:
                del report_data['results'][_python][_ser]

    # Generate index HTML
    with open(os.path.join(output, 'index.html'), 'w') as f:
        s = template_index.render(
            naturalsize=humanize.naturalsize,
            intword=humanize.intword,
            intcomma=humanize.intcomma,
            sorted=sorted,
            **report_data
        )
        f.write(s)

    print(f'Report generated: {os.path.join(output, "index.html")}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='WAMP Message Serialization Benchmarks'
    )
    subparsers = parser.add_subparsers(
        dest='command',
        title='commands',
        help='Command to run (required)'
    )
    subparsers.required = True

    # Run benchmark subcommand
    parser_run = subparsers.add_parser(
        'run',
        help='Run serialization benchmark'
    )

    parser_run.add_argument(
        '--iterations',
        dest='iterations',
        type=int,
        default=10,
        help='Number of iterations in the benchmarking loop (default: 10)'
    )

    parser_run.add_argument(
        '--serializer',
        dest='serializer',
        choices=['json', 'cbor', 'msgpack', 'ubjson', 'flatbuffers'],
        default='cbor',
        help='Serializer to use (implementation variants like ujson/json or cbor2/cbor '
             'can be selected via AUTOBAHN_USE_UJSON or AUTOBAHN_USE_CBOR2 env vars)'
    )

    parser_run.add_argument(
        '--payload_mode',
        dest='payload_mode',
        choices=['normal', 'transparent'],
        default='normal',
        help='WAMP payload mode: normal (args) or transparent (payload)'
    )

    parser_run.add_argument(
        '--payload_size',
        dest='payload_size',
        choices=['empty', 'small', 'medium', 'large', 'xl', 'xxl'],
        default='small',
        help='Payload size category'
    )

    parser_run.add_argument(
        '--profile',
        dest='profile',
        type=str,
        required=True,
        help='vmprof profile output filename (.dat)'
    )

    parser_run.add_argument(
        '--results',
        dest='results',
        type=str,
        required=True,
        help='Results output directory'
    )

    parser_run.set_defaults(func=main_run)

    # Index generation subcommand
    parser_index = subparsers.add_parser(
        'index',
        help='Generate HTML report index from benchmark results'
    )

    parser_index.add_argument(
        '--output',
        dest='output',
        type=str,
        required=True,
        help='Output directory for HTML report'
    )

    parser_index.set_defaults(func=main_index)

    args = parser.parse_args()
    args.func(args)
