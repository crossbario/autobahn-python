#!/bin/bash
# Generate flamegraph SVGs from vmprof profile data
# Requires: vmprof-flamegraph Python package and Perl (for flamegraph.pl)
set -e

BUILD_DIR="${1:-build}"
VENV_PYTHON="${2:-.venvs/cpy311/bin/python3}"

echo "=============================================="
echo "Generating flamegraph SVGs from vmprof profiles"
echo "=============================================="
echo "Build directory: $BUILD_DIR"
echo "Using Python: $VENV_PYTHON"
echo ""

# Convert relative paths to absolute if needed
if [[ "$BUILD_DIR" != /* ]]; then
    BUILD_DIR="$(pwd)/$BUILD_DIR"
fi
if [[ "$VENV_PYTHON" != /* ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../../.. && pwd)"
    VENV_PYTHON="$SCRIPT_DIR/$VENV_PYTHON"
fi

# Get the directory where this script is located (for flamegraph.pl)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLAMEGRAPH_PL="$SCRIPT_DIR/flamegraph.pl"

# Check if Perl is available
if ! command -v perl >/dev/null 2>&1; then
    echo "❌ ERROR: Perl not found. Flamegraph generation requires Perl."
    exit 1
fi

# Check if flamegraph.pl exists
if [ ! -f "$FLAMEGRAPH_PL" ]; then
    echo "❌ ERROR: flamegraph.pl not found at $FLAMEGRAPH_PL"
    echo "Please download it from: https://raw.githubusercontent.com/brendangregg/FlameGraph/master/flamegraph.pl"
    exit 1
fi

# Check if vmprof-flamegraph is available
VENV_BIN_DIR="$(dirname "$VENV_PYTHON")"
VMPROF_FLAMEGRAPH="$VENV_BIN_DIR/vmprof-flamegraph.py"
if [ ! -f "$VMPROF_FLAMEGRAPH" ]; then
    echo "❌ ERROR: vmprof-flamegraph.py not found at $VMPROF_FLAMEGRAPH"
    echo "Please run: just install-benchmark <venv>"
    exit 1
fi

cd "$BUILD_DIR"

COUNT=0
SKIPPED=0
FAILED=0

for dat_file in profile_*.dat; do
    if [ -f "$dat_file" ]; then
        # Extract base name (e.g., profile_cbor_normal_small.dat -> cbor_normal_small)
        base=$(basename "$dat_file" .dat)
        base=${base#profile_}
        svg_file="vmprof_${base}.svg"

        if [ -f "$svg_file" ]; then
            # Skip existing flamegraphs
            SKIPPED=$((SKIPPED + 1))
        else
            echo -n "Generating $svg_file from $dat_file..."
            # Generate flamegraph (suppress stderr which may have warnings)
            set +e
            $VMPROF_FLAMEGRAPH --prune_level=900 --prune_percent=0.001 "$dat_file" 2>/dev/null | \
               $FLAMEGRAPH_PL --colors hot --bgcolor=grey --width=1200 --height=16 --fonttype=sans --fontsize=11 2>/dev/null > "$svg_file"
            EXIT_CODE=${PIPESTATUS[0]}  # Get exit code of vmprof-flamegraph
            set -e

            # Check if SVG was generated successfully (exists and is not empty)
            if [ -f "$svg_file" ] && [ -s "$svg_file" ]; then
                echo " ✓"
                COUNT=$((COUNT + 1))
            else
                echo " ✗ (failed, exit code: $EXIT_CODE)"
                FAILED=$((FAILED + 1))
                # Remove incomplete/empty SVG file
                rm -f "$svg_file"
            fi
        fi
    fi
done

echo ""
echo "=============================================="
echo "✅ Generated: $COUNT flamegraph SVG files"
if [ $SKIPPED -gt 0 ]; then
    echo "⏭️  Skipped: $SKIPPED existing flamegraphs"
fi
if [ $FAILED -gt 0 ]; then
    echo "❌ Failed: $FAILED flamegraphs"
fi
echo "=============================================="
