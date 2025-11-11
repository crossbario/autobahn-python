# WAMP Message Serialization Benchmarks

Comprehensive performance benchmarking suite for WAMP message serialization/deserialization across multiple serializers, payload modes, and payload sizes.

## Overview

This benchmark suite measures the serialization and deserialization performance of WAMP messages using real-world vehicle telemetry data. It provides detailed performance metrics and CPU profiling with flamegraph visualization.

### Key Features

- **Multi-dimensional testing matrix**:
  - 7 serializers: json, ujson, msgpack, cbor, cbor2, ubjson, flatbuffers
  - 2 payload modes: normal (WAMP args), transparent (WAMP payload)
  - 6 payload sizes: empty, small, medium, large, xl (16KB), xxl (128KB)
  - 2 Python implementations: CPython, PyPy

- **Performance profiling**:
  - vmprof statistical profiling (0.01s period)
  - Flamegraph visualization
  - Warm-up phase before measurement

- **Real-world data**:
  - Vehicle telemetry from CSV datasets (7MB)
  - GPS coordinates, sensor data, timestamps
  - Deterministic pseudo-random pothole sensor data

- **Comprehensive reporting**:
  - JSON results with msgs/sec, bytes/sec, avg message size
  - HTML report index with tabular results
  - Individual flamegraph HTML pages per configuration

## Usage

### Prerequisites

Install Autobahn|Python with development dependencies:

```bash
pip install -e ".[dev,compress,nvx]"
```

Required dependencies:
- `vmprof>=0.4.15` - Statistical profiling
- `jinja2>=3.0.0` - HTML template rendering
- `humanize>=4.0.0` - Human-readable formatting
- `cbor2` - CBOR serializer (batteries-included)

### Running Benchmarks

#### 1. Run a Single Benchmark

```bash
python main.py run \
    --serializer cbor \
    --payload_mode normal \
    --payload_size small \
    --iterations 10 \
    --profile build/profile.dat \
    --results build
```

**Parameters**:
- `--serializer`: Choose from `json`, `cbor`, `msgpack`, `ubjson`, `flatbuffers`
  - Use `AUTOBAHN_USE_UJSON=1` env var to select ujson instead of json
  - Use `AUTOBAHN_USE_CBOR2=1` env var to select cbor2 instead of cbor
- `--payload_mode`: `normal` (WAMP args) or `transparent` (WAMP payload)
- `--payload_size`: `empty`, `small`, `medium`, `large`, `xl`, `xxl`
- `--iterations`: Number of benchmark iterations (default: 10)
- `--profile`: Output path for vmprof profile data (.dat file)
- `--results`: Output directory for JSON results

**Output files**:
- `build/profile.dat` - vmprof profiling data
- `build/results_cpy_cbor_normal_small.json` - JSON results with metrics

#### 2. Generate HTML Report

After running multiple benchmarks:

```bash
python main.py index --output build
```

This generates:
- `build/index.html` - Main report with tabular results
- `build/vmprof_cpy_cbor_normal_small.html` - Individual flamegraph pages

**View the report**:

```bash
# Open in browser
xdg-open build/index.html
# or
python -m http.server 8000 -d build
# then visit http://localhost:8000
```

### Example: Full Benchmark Run

Run benchmarks for all serializers with small payload:

```bash
mkdir -p build

for serializer in json msgpack cbor ubjson flatbuffers; do
    for mode in normal transparent; do
        echo "Running: $serializer, $mode, small"
        python main.py run \
            --serializer $serializer \
            --payload_mode $mode \
            --payload_size small \
            --iterations 10 \
            --profile build/profile_${serializer}_${mode}.dat \
            --results build
    done
done

# Test ujson variant
AUTOBAHN_USE_UJSON=1 python main.py run \
    --serializer json \
    --payload_mode normal \
    --payload_size small \
    --iterations 10 \
    --profile build/profile_ujson_normal.dat \
    --results build

# Generate HTML report
python main.py index --output build
```

### Using Just Recipes (Recommended)

If you have [Just](https://just.systems/) installed:

```bash
# Run benchmark with specific configuration
just benchmark-serialization-run cbor normal small

# Run full benchmark suite
just benchmark-serialization-suite

# Generate HTML report
just benchmark-serialization-report

# Clean benchmark artifacts
just benchmark-serialization-clean
```

See `justfile` in repository root for recipe definitions.

## Payload Sizes

The benchmark suite tests 6 different payload sizes:

| Size | Description | Approximate Size |
|------|-------------|------------------|
| `empty` | Minimal empty payload | ~0 bytes |
| `small` | Base vehicle telemetry (GPS, sensors) | ~200-300 bytes |
| `medium` | Small + JSON_DATA1 (widget config) | ~500-800 bytes |
| `large` | Medium + JSON_DATA2 (actors) + JSON_DATA3 (nested donuts) | ~1-2 KB |
| `xl` | Small + 16KB binary frame | ~16 KB |
| `xxl` | Small + 128KB binary frame | ~128 KB |

## Performance Metrics

For each configuration, the benchmark measures:

- **msgs_per_sec**: Throughput in messages per second
- **bytes_per_sec**: Bandwidth in bytes per second
- **msg_bytes**: Average serialized message size in bytes

Results are saved in JSON format:

```json
{
    "python_version": "3.11.2 (main, ...)",
    "python": "cpy",
    "events": 1234,
    "sample": { ... },
    "iterations": 10,
    "msg_bytes": 256,
    "msgs_per_sec": 123456,
    "bytes_per_sec": 31604736
}
```

## CPU Profiling with vmprof

The benchmark uses vmprof for statistical profiling during the measurement phase:

- **Sampling period**: 0.01 seconds (100 samples/sec)
- **Output format**: vmprof .dat files
- **Visualization**: Convert to flamegraph SVG using vmprof web interface or tooling

Flamegraph HTML pages show:
- Function call hierarchy
- Time spent in each function
- Hot paths in serialization code

This helps identify performance bottlenecks in:
- WAMP message construction
- Serializer encode/decode operations
- Data structure traversal
- Memory allocation patterns

## Data Sources

### Vehicle Telemetry CSV Datasets

The benchmark uses two CSV datasets with real vehicle telemetry:

- `data/dataset1.csv` (~1MB) - Fleet 1 vehicles
- `data/dataset2.csv` (~6MB) - Fleet 2 vehicles

**CSV columns**:
- `vehicleID` - Vehicle identifier
- `ts` - Timestamp (YYYY-MM-DD HH:MM:SS)
- `lon`, `lat` - GPS coordinates
- `speed` - Vehicle speed
- `rain` - Rain sensor value
- `dyn_wiper` - Wiper status

**Derived fields**:
- `xtile`, `ytile` - Tile coordinates (zoom level 18)
- `pothole_depth` - Deterministic pseudo-random (0.0-1.0)
- `pothole_type` - Random choice from type-a through type-f

### Sample JSON Data Structures

Additional JSON structures from `sample.py` are used to increase payload sizes:

- `JSON_DATA1` - JSON:API article structure with widget configuration
- `JSON_DATA2` - Actor information (Tom Cruise, Robert Downey Jr.)
- `JSON_DATA3` - Nested donut menu with batters and toppings

## Directory Structure

```
examples/benchmarks/serialization/
├── README.md                  # This file
├── main.py                    # Benchmark runner with vmprof profiling
├── loader.py                  # CSV data loader and VehicleEvent class
├── sample.py                  # Sample JSON data structures
├── data/
│   ├── dataset1.csv          # Fleet 1 vehicle telemetry (1MB)
│   └── dataset2.csv          # Fleet 2 vehicle telemetry (6MB)
├── templates/
│   ├── base.html             # Jinja2 base template
│   ├── index.html            # Main report template
│   └── flamegraph.html       # Flamegraph page template
├── crossbarfx_black.svg      # Logo for HTML reports
└── build/                     # Generated artifacts (gitignored)
    ├── *.json                # JSON results per configuration
    ├── *.dat                 # vmprof profile data
    ├── *.html                # HTML report and flamegraphs
    └── *.svg                 # Flamegraph SVG (if generated)
```

## Integration with CI/CD

This benchmark suite is integrated into the GitHub Actions workflow at `.github/workflows/benchmark-serialization.yml`:

- Runs on CPython and PyPy (x86-64)
- Tests all serializers and payload configurations
- Publishes results as workflow artifacts
- Integrates artifacts into Read the Docs documentation

See workflow file for configuration details.

## Tips and Best Practices

### For Accurate Results

1. **Close other applications** to minimize CPU contention
2. **Run multiple iterations** (at least 10) for statistical validity
3. **Use production-like data** - the CSV datasets simulate real workloads
4. **Compare apples to apples** - same payload_mode and payload_size across serializers
5. **Test both CPython and PyPy** - performance characteristics differ significantly

### Expected Performance Characteristics

- **PyPy** typically shows 2-10x higher throughput than CPython due to JIT compilation
- **Binary serializers** (msgpack, cbor, flatbuffers) are usually faster than JSON
- **Transparent payload mode** may show different characteristics than normal mode
- **Larger payloads** (xl, xxl) stress different code paths than small payloads

### Troubleshooting

**ImportError: No module named 'vmprof'**
```bash
pip install vmprof
```

**FileNotFoundError: data/dataset1.csv**
```bash
# Ensure you're running from examples/benchmarks/serialization/
cd examples/benchmarks/serialization
python main.py run ...
```

**PermissionError on vmprof profile file**
```bash
# Ensure build directory exists and is writable
mkdir -p build
chmod 755 build
```

## Further Reading

- [WAMP Specification](https://wamp-proto.org/)
- [Autobahn|Python Documentation](https://autobahn.readthedocs.io/)
- [vmprof Documentation](https://vmprof.readthedocs.io/)
- [Performance Optimization Guide](https://autobahn.readthedocs.io/en/latest/performance.html)

## License

MIT License - See LICENSE file in repository root.

Copyright (c) typedef int GmbH
