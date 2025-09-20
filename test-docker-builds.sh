#!/bin/bash
# Test script for Docker-based wheel building
# Usage: ./test-docker-builds.sh [BASE_IMAGE] [PLATFORM]

set -e

BASE_IMAGE=${1:-"debian:12"}
PLATFORM=${2:-"linux/amd64"}
TEST_OUTPUT_DIR="./test-dist"

echo "=========================================="
echo "Testing Docker wheel building"
echo "=========================================="
echo "Base Image: $BASE_IMAGE"
echo "Platform: $PLATFORM"
echo "Output: $TEST_OUTPUT_DIR"
echo ""

# Clean previous test results
rm -rf "$TEST_OUTPUT_DIR"
mkdir -p "$TEST_OUTPUT_DIR"

echo "==> Setting up Docker Buildx..."
docker buildx create --use --name autobahn-builder 2>/dev/null || docker buildx use autobahn-builder

echo ""
echo "==> Building wheels with Docker..."
docker buildx bake \
  --set wheel-builder.platform="$PLATFORM" \
  --set wheel-builder.args.BASE_IMAGE="$BASE_IMAGE" \
  --set wheel-builder.output="type=local,dest=$TEST_OUTPUT_DIR" \
  wheel-builder

echo ""
echo "==> Build Results:"
echo "=================="

if [ -d "$TEST_OUTPUT_DIR" ]; then
  echo "Files created:"
  ls -la "$TEST_OUTPUT_DIR/"
  
  echo ""
  echo "Build metadata:"
  echo "==============="
  if [ -f "$TEST_OUTPUT_DIR/build-info.txt" ]; then
    cat "$TEST_OUTPUT_DIR/build-info.txt"
  else
    echo "No build-info.txt found"
  fi
  
  echo ""
  echo "Wheels summary:"
  echo "==============="
  wheel_count=$(find "$TEST_OUTPUT_DIR" -name "*.whl" 2>/dev/null | wc -l)
  echo "Total wheels: $wheel_count"
  
  if [ "$wheel_count" -gt 0 ]; then
    echo "Wheel files:"
    find "$TEST_OUTPUT_DIR" -name "*.whl" -exec basename {} \; | sort
    
    echo ""
    echo "Testing wheel installability:"
    echo "============================="
    
    # Test one wheel installation in a temporary container
    if wheel_file=$(find "$TEST_OUTPUT_DIR" -name "*cp312*.whl" | head -1); then
      echo "Testing installation of: $(basename "$wheel_file")"
      
      docker run --rm -v "$(pwd)/$wheel_file:/test.whl" python:3.12-slim bash -c "
        pip install /test.whl && 
        python -c 'import autobahn; print(f\"autobahn version: {autobahn.__version__}\")' &&
        echo 'Wheel installation test: PASSED'
      " || echo "Wheel installation test: FAILED"
    fi
  fi
else
  echo "ERROR: No output directory created"
  exit 1
fi

echo ""
echo "==> Test completed successfully!"
echo ""
echo "To test other configurations:"
echo "  ./test-docker-builds.sh debian:12 linux/arm64"
echo "  ./test-docker-builds.sh rockylinux:9 linux/amd64" 
echo "  ./test-docker-builds.sh ubuntu:24.04 linux/amd64"