#!/bin/bash
# RTD Build Script: Download conformance artifacts from GitHub Releases
# This script runs during Read the Docs builds to fetch WebSocket conformance
# test results that are generated during CI and uploaded to GitHub Releases.

set -e

echo "========================================================================"
echo "RTD Artifact Download Script"
echo "========================================================================"

# GitHub repository details
GITHUB_REPO="crossbario/autobahn-python"
GITHUB_API="https://api.github.com/repos/${GITHUB_REPO}"

# Determine which version/tag we're building
# RTD sets READTHEDOCS_VERSION (e.g., "latest", "stable", "v25.9.1")
RTD_VERSION="${READTHEDOCS_VERSION:-unknown}"
echo "RTD Version: ${RTD_VERSION}"
echo ""

# Determine release tag to download from
RELEASE_TAG=""

if [[ "${RTD_VERSION}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    # Building a specific version tag (e.g., v25.9.1)
    RELEASE_TAG="${RTD_VERSION}"
    echo "Building specific version: ${RELEASE_TAG}"
elif [[ "${RTD_VERSION}" == "latest" ]]; then
    # "latest" points to the most recent commit on master
    # Use the latest tag for artifacts
    echo "Building 'latest' - fetching most recent release tag..."
    RELEASE_TAG=$(curl -s "${GITHUB_API}/releases/latest" | grep '"tag_name":' | sed -E 's/.*"tag_name": "([^"]+)".*/\1/')
    echo "Latest release tag: ${RELEASE_TAG}"
elif [[ "${RTD_VERSION}" == "stable" ]]; then
    # "stable" should point to the latest stable release
    echo "Building 'stable' - fetching most recent release tag..."
    RELEASE_TAG=$(curl -s "${GITHUB_API}/releases/latest" | grep '"tag_name":' | sed -E 's/.*"tag_name": "([^"]+)".*/\1/')
    echo "Stable release tag: ${RELEASE_TAG}"
else
    # Unknown version (development branch, etc.)
    echo "⚠️  Unknown RTD version '${RTD_VERSION}'"
    echo "⚠️  Skipping conformance artifact download (only available for releases)"
    exit 0
fi

if [ -z "${RELEASE_TAG}" ]; then
    echo "⚠️  Could not determine release tag, skipping artifact download"
    exit 0
fi

echo ""
echo "========================================================================"
echo "Downloading conformance artifacts for release: ${RELEASE_TAG}"
echo "========================================================================"
echo ""

# Create target directory for conformance reports
TARGET_DIR="docs/_static/websocket/conformance"
mkdir -p "${TARGET_DIR}"

# Download conformance artifacts from GitHub Release
# The release workflow uploads these as: autobahn-python-websocket-conformance-{tag}.tar.gz
CONFORMANCE_ARTIFACT="autobahn-python-websocket-conformance-${RELEASE_TAG}.tar.gz"
CONFORMANCE_URL="https://github.com/${GITHUB_REPO}/releases/download/${RELEASE_TAG}/${CONFORMANCE_ARTIFACT}"

echo "==> Downloading conformance artifact..."
echo "    URL: ${CONFORMANCE_URL}"
echo "    Target: ${TARGET_DIR}/"
echo ""

# Download with curl (follow redirects, show progress)
if curl -L -f -o "/tmp/${CONFORMANCE_ARTIFACT}" "${CONFORMANCE_URL}"; then
    echo "✅ Conformance artifact downloaded successfully"
    echo ""

    # Extract tarball to target directory
    echo "==> Extracting conformance reports..."
    tar -xzf "/tmp/${CONFORMANCE_ARTIFACT}" -C "${TARGET_DIR}"

    echo "✅ Extraction complete"
    echo ""

    # Show what was extracted
    echo "==> Extracted conformance files:"
    find "${TARGET_DIR}" -type f | head -20
    echo ""

    # Cleanup
    rm -f "/tmp/${CONFORMANCE_ARTIFACT}"
else
    echo "⚠️  Failed to download conformance artifact"
    echo "⚠️  This is expected for releases without conformance reports"
    echo "⚠️  Sphinx build will continue without conformance test results"
    echo ""
fi

# Download FlatBuffers schema artifacts from GitHub Release
# The release workflow uploads these as: flatbuffers-schema.tar.gz
FLATBUFFERS_ARTIFACT="flatbuffers-schema.tar.gz"
FLATBUFFERS_URL="https://github.com/${GITHUB_REPO}/releases/download/${RELEASE_TAG}/${FLATBUFFERS_ARTIFACT}"
FLATBUFFERS_TARGET="docs/_static/flatbuffers"

echo ""
echo "========================================================================"
echo "==> Downloading FlatBuffers schema artifact..."
echo "    URL: ${FLATBUFFERS_URL}"
echo "========================================================================"
echo ""

mkdir -p "${FLATBUFFERS_TARGET}"

if curl -L -f -o "/tmp/${FLATBUFFERS_ARTIFACT}" "${FLATBUFFERS_URL}"; then
    echo "✅ FlatBuffers artifact downloaded successfully"
    echo ""

    # Extract tarball to target directory
    echo "==> Extracting FlatBuffers schema files..."
    tar -xzf "/tmp/${FLATBUFFERS_ARTIFACT}" -C "${FLATBUFFERS_TARGET}"

    echo "✅ Extraction complete"
    echo ""

    # Show what was extracted
    echo "==> Extracted FlatBuffers files:"
    find "${FLATBUFFERS_TARGET}" -type f | head -20
    echo ""

    # Cleanup
    rm -f "/tmp/${FLATBUFFERS_ARTIFACT}"
else
    echo "⚠️  Failed to download FlatBuffers artifact"
    echo "⚠️  This is expected for releases without FlatBuffers schema docs"
    echo ""
fi

echo ""
echo "========================================================================"
echo "✅ All documentation artifacts processed"
echo "========================================================================"
