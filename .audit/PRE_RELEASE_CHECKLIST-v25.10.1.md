# Pre-Release Testing Checklist for v25.10.1

This checklist ensures everything works locally before pushing to PyPI.

## 1. Package Build & Contents Verification

### 1.1 Build the package

```bash
# Clean previous builds
just distclean

# Build with current branch
just build-all

# Verify artifacts created
ls -lh dist/

# Expected:
# autobahn-25.10.1-cp311-cp311-linux_x86_64.whl
# autobahn-25.10.1-cp312-cp312-linux_x86_64.whl
# autobahn-25.10.1-cp313-cp313-linux_x86_64.whl
# autobahn-25.10.1-cp314-cp314-linux_x86_64.whl
# autobahn-25.10.1-pp311-pypy311_pp73-linux_x86_64.whl
# autobahn-25.10.1.tar.gz
```

### 1.2 Verify source distribution contents

```bash
# List contents
tar -tzf dist/autobahn-25.10.1.tar.gz | head -50

# Check FlatBuffers are included
tar -tzf dist/autobahn-25.10.1.tar.gz | grep -E "(\.fbs|\.bfbs|wamp/gen.*\.py)"

# Expected:
#   autobahn-25.10.1/autobahn/wamp/flatbuffers/*.fbs (7 files)
#   autobahn-25.10.1/autobahn/wamp/gen/schema/*.bfbs (7 files)
#   autobahn-25.10.1/autobahn/wamp/gen/**/*.py (65+ files)
```

### 1.3 Verify wheel contents

```bash
# Extract and list wheel contents
for whl in dist/*.whl; do
  echo "=== $(basename "$whl") ==="
  unzip -l "$whl" \
    | grep -E "(wamp/gen|flatbuffers|\.fbs|\.bfbs)" \
    | awk -F. '{print $NF}' \
    | sort \
    | uniq -c \
    | sort -nr
  echo
done

# Expected:
# === autobahn-25.10.1-cp311-cp311-linux_x86_64.whl ===
#      65 py
#       7 fbs
#       7 bfbs
#
# === autobahn-25.10.1-cp312-cp312-linux_x86_64.whl ===
#      65 py
#       7 fbs
#       7 bfbs
#
# === autobahn-25.10.1-cp313-cp313-linux_x86_64.whl ===
#      65 py
#       7 fbs
#       7 bfbs
#
# === autobahn-25.10.1-cp314-cp314-linux_x86_64.whl ===
#      65 py
#       7 fbs
#       7 bfbs
#
# === autobahn-25.10.1-pp311-pypy311_pp73-linux_x86_64.whl ===
#      65 py
#       7 fbs
#       7 bfbs
```

### 1.4 Verify source distribution integrity

```bash
# Run the same checks as CI
gzip -tv dist/autobahn-25.10.1.tar.gz
tar -tzf dist/autobahn-25.10.1.tar.gz > /dev/null

# Compute SHA256
openssl sha256 dist/autobahn-25.10.1.tar.gz
```

## 2. Local Installation & Import Tests

### 2.1 Install in clean virtualenv

```bash
# Create fresh test environment
python3 -m venv /tmp/test_autobahn_v25.10.1
source /tmp/test_autobahn_v25.10.1/bin/activate

# Install from local wheel - minimal!
pip install --find-links=dist autobahn

# Or install from source dist
# pip install dist/autobahn-25.10.1.tar.gz

# Install from local wheel - full!
pip install --find-links=dist autobahn[all]

# Expected:
# Looking in links: dist
# Processing ./dist/autobahn-25.10.1-cp312-cp312-linux_x86_64.whl

# IMPORTANT: make sure we do _not_ accidentily import modules from source tree (git working repo), aka Python "development mode"!
cd ~
```

### 2.2 Test basic import

```bash
python -c 'import autobahn; print(f"✅ Autobahn version: {autobahn.__version__}")'
```

### 2.3 Test Flatbuffers run-time imports

```bash
python3 << 'EOF'
# Test FlatBuffers wrapper imports
from autobahn.wamp.gen.wamp.proto import Welcome
print(f"✅ Welcome class: {Welcome}")

from autobahn.wamp.gen.wamp.proto import Hello, Goodbye, Error
print(f"✅ Core WAMP messages: Hello, Goodbye, Error")

print("\n✅ ALL IMPORTS SUCCESSFUL")
EOF
```

**Expected output:**

```
✅ Welcome class: <module 'autobahn.wamp.gen.wamp.proto.Welcome' from '/tmp/test_autobahn_v25.10.1/lib/python3.12/site-packages/autobahn/wamp/gen/wamp/proto/Welcome.py'>
✅ Core WAMP messages: Hello, Goodbye, Error

✅ ALL IMPORTS SUCCESSFUL
```

### 2.4 Test Flatbuffers schemata (source & binary) file access

**IMPORTANT:** Use `importlib.resources` to access package data files correctly.
This works with both installed wheels and development installs, unlike `__file__`.

```bash
python3 << 'EOF'
# Modern way to access package data files (Python 3.9+)
try:
    from importlib.resources import files
except ImportError:
    # Fallback for Python 3.7-3.8 (if needed)
    from importlib_resources import files

# Test binary schema access
schema_pkg = files('autobahn.wamp.gen.schema')
bfbs_files = sorted([f.name for f in schema_pkg.iterdir() if f.name.endswith('.bfbs')])
print(f"✅ Binary schemas found: {len(bfbs_files)} files")
print(f"   Files: {bfbs_files}")

# Test source schema access
fbs_pkg = files('autobahn.wamp.flatbuffers')
fbs_files = sorted([f.name for f in fbs_pkg.iterdir() if f.name.endswith('.fbs')])
print(f"✅ Source schemas found: {len(fbs_files)} files")
print(f"   Files: {fbs_files}")

# Test actual file reading
test_file = schema_pkg.joinpath('wamp.bfbs')
if test_file.is_file():
    data = test_file.read_bytes()
    print(f"✅ Can read binary schema: wamp.bfbs ({len(data)} bytes)")
else:
    print(f"❌ ERROR: wamp.bfbs not found!")

print("\n✅ ALL SCHEMA FILE ACCESSES SUCCESSFUL")
EOF
```

**Expected output:**

```
✅ Binary schemas found: 7 files
   Files: ['auth.bfbs', 'pubsub.bfbs', 'roles.bfbs', 'rpc.bfbs', 'session.bfbs', 'types.bfbs', 'wamp.bfbs']
✅ Source schemas found: 7 files
   Files: ['auth.fbs', 'pubsub.fbs', 'roles.fbs', 'rpc.fbs', 'session.fbs', 'types.fbs', 'wamp.fbs']
✅ Can read binary schema: wamp.bfbs (28648 bytes)

✅ ALL SCHEMA FILE ACCESSES SUCCESSFUL
```

### 2.5 Test runtime functionality

```bash
python3 << 'EOF'
# Test basic WAMP functionality
from autobahn.wamp import types

# Test with FlatBuffers
from autobahn.wamp.gen.wamp.proto import Hello
print(f"✅ Can instantiate WAMP message classes")

# Test serialization extras if installed
try:
    import flatbuffers
    print(f"✅ flatbuffers available: {flatbuffers.__version__}")
except ImportError:
    print("⚠️  flatbuffers not installed (install with: pip install 'autobahn[serialization]')")

print("\n✅ RUNTIME TESTS PASSED")
EOF
```

**Expected output:**

```
✅ Can instantiate WAMP message classes
✅ flatbuffers available: 25.9.23

✅ RUNTIME TESTS PASSED
```

### 2.6 Cleanup test environment

```bash
deactivate
rm -rf /tmp/test_autobahn_v25.10.1
```

## 3. Run Checks & Unit tests

### 3.1 Formatting

```
just check-format
```

**Expected output:**

```
...
==> Defaulting to venv: 'cpy312'
==> Linting code with cpy312...
All checks passed!
```

### 3.2 Typing

```
just check-typing
```

**Expected output:**

```
...
Found 247 errors in 44 files (checked 164 source files)
error: Recipe `check-typing` failed with exit code 1
```

### 3.3 Unit Tests

#### Twisted

```
just test-twisted
```

**Expected output:**

```
...
-------------------------------------------------------------------------------
Ran 328 tests in 2.987s

PASSED (skips=27, successes=301)
```

#### Asyncio

```
just test-asyncio
```

**Expected output:**

```
...
========================================= 226 passed, 3 skipped, 6 warnings in 4.54s ==========================================
```

## 4. Run coverage

### 4.1 Twisted

```
just check-coverage-twisted
```

**Expected output:**

```
...
-------------------------------------------------------------------------------
Ran 328 tests in 4.305s

PASSED (skips=27, successes=301)
```

### 4.2 asyncio

```
just check-coverage-asyncio
```

**Expected output:**

```
...
========================================= 226 passed, 3 skipped, 6 warnings in 6.09s ==========================================
```

## 5. Run conformance tests

### 5.1 Testee Clients

*Terminal 1:*

```
just wstest-fuzzingserver
```

*Terminal 2:*

```
just wstest-testeeclient-twisted
just wstest-testeeclient-asyncio
```

**Expected output:**

```
oberstet@amd-ryzen5:~/scm/crossbario/autobahn-python$ tree .wstest/clients
.wstest/
└── clients
    ├── autobahn_25_9_1_nvxcffi_2_0_0_asyncio_cpython_3_12_11_case_1_1_1.html
    ├── autobahn_25_9_1_nvxcffi_2_0_0_asyncio_cpython_3_12_11_case_1_1_1.json
    ├── autobahn_25_9_1_nvxcffi_2_0_0_asyncio_cpython_3_12_11_case_1_1_2.html
    ├── autobahn_25_9_1_nvxcffi_2_0_0_asyncio_cpython_3_12_11_case_1_1_2.json
...
    ├── autobahn_25_9_1_nvxcffi_2_0_0_twisted_25_5_0_cpython_3_12_11_case_1_1_1.html
    ├── autobahn_25_9_1_nvxcffi_2_0_0_twisted_25_5_0_cpython_3_12_11_case_1_1_1.json
    ├── autobahn_25_9_1_nvxcffi_2_0_0_twisted_25_5_0_cpython_3_12_11_case_1_1_2.html
    ├── autobahn_25_9_1_nvxcffi_2_0_0_twisted_25_5_0_cpython_3_12_11_case_1_1_2.json
...
    ├── index.html
    └── index.json

2 directories, 986 files
oberstet@amd-ryzen5:~/scm/crossbario/autobahn-python$ cloc .wstest/clients
 986 text files.
 986 unique files.
   0 files ignored.

github.com/AlDanial/cloc v 1.98  T=0.86 s (1148.7 files/s, 296672.1 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
HTML                           493          17756              0         140555
JSON                           493              0              0          96350
-------------------------------------------------------------------------------
SUM:                           986          17756              0         236905
-------------------------------------------------------------------------------
oberstet@amd-ryzen5:~/scm/crossbario/autobahn-python$
```

### 5.2 Testee Servers

*Terminal 1:*

```
just wstest-testeeserver-twisted
```

*Terminal 2:*

```
just wstest-testeeserver-asyncio
```

*Terminal 3:*

```
just wstest-fuzzingclient
```

**Expected output:**

```
oberstet@amd-ryzen5:~/scm/crossbario/autobahn-python$ tree .wstest/servers/
.wstest/servers/
├── autobahn_25_9_1_nvxcffi_2_0_0_asyncio_cpython_3_12_11_case_1_1_1.html
├── autobahn_25_9_1_nvxcffi_2_0_0_asyncio_cpython_3_12_11_case_1_1_1.json
├── autobahn_25_9_1_nvxcffi_2_0_0_asyncio_cpython_3_12_11_case_1_1_2.html
├── autobahn_25_9_1_nvxcffi_2_0_0_asyncio_cpython_3_12_11_case_1_1_2.json
...
├── autobahn_25_9_1_nvxcffi_2_0_0_twisted_25_5_0_cpython_3_12_11_case_1_1_1.html
├── autobahn_25_9_1_nvxcffi_2_0_0_twisted_25_5_0_cpython_3_12_11_case_1_1_1.json
├── autobahn_25_9_1_nvxcffi_2_0_0_twisted_25_5_0_cpython_3_12_11_case_1_1_2.html
├── autobahn_25_9_1_nvxcffi_2_0_0_twisted_25_5_0_cpython_3_12_11_case_1_1_2.json
...
├── index.html
└── index.json
oberstet@amd-ryzen5:~/scm/crossbario/autobahn-python$ cloc .wstest/servers/
     986 text files.
     986 unique files.
       0 files ignored.

github.com/AlDanial/cloc v 1.98  T=0.89 s (1110.7 files/s, 286734.2 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
HTML                           493          17756              0         139618
JSON                           493              0              0          97178
-------------------------------------------------------------------------------
SUM:                           986          17756              0         236796
-------------------------------------------------------------------------------
oberstet@amd-ryzen5:~/scm/crossbario/autobahn-python$
```

## 6. Download GitHub Release Artifacts

Download GitHub Release Artifacts for local docs testing:

* WebSocket Compliance Reports
* FlatBuffers Schemata

**Note:** By default, we download from the **latest nightly release** (not the latest stable release).
This ensures we're testing the artifacts that will become the next stable release after successful testing.

```bash
# Download latest nightly release artifacts
just download-github-release
```

**Alternative usage:**

```bash
# Download latest stable release
just download-github-release stable

# Download latest development release
just download-github-release dev

# Download specific release tag
just download-github-release v25.10.1
```

**Expected output:**

```
==> Downloading GitHub release artifacts for: nightly

==> Finding latest nightly release (tagged as master-YYYYMMDDHHMM)...
✅ Found nightly release: master-202510180103

==> Downloading WebSocket conformance reports...
✅ Downloaded: autobahn-python-websocket-conformance-master-202510180103.tar.gz

==> Downloading FlatBuffers schemas...
✅ Downloaded: flatbuffers-schema.tar.gz

==> Extracting artifacts...
✅ Extracted conformance reports
✅ Extracted FlatBuffers schemas

==> Downloaded and extracted artifacts:
total 8.1M
-rw-r--r-- 1 user user 8.0M Oct 18 01:03 conformance.tar.gz
-rw-r--r-- 1 user user  32K Oct 18 01:03 flatbuffers-schema.tar.gz
drwxr-xr-x 2 user user 4.0K Oct 18 01:03 with-nvx/
drwxr-xr-x 2 user user 4.0K Oct 18 01:03 without-nvx/
-rw-r--r-- 1 user user  20K Oct 18 01:03 wamp.fbs
-rw-r--r-- 1 user user  28K Oct 18 01:03 wamp.bfbs
... (more schema files)

════════════════════════════════════════════════════════════
✅ Artifacts downloaded to: /tmp/autobahn-release-artifacts-master-202510180103
════════════════════════════════════════════════════════════

Release: master-202510180103
Location: /tmp/autobahn-release-artifacts-master-202510180103

To use these artifacts:
  - Conformance reports: /tmp/autobahn-release-artifacts-master-202510180103/with-nvx/, /tmp/autobahn-release-artifacts-master-202510180103/without-nvx/
  - FlatBuffers schemas: /tmp/autobahn-release-artifacts-master-202510180103/*.fbs, /tmp/autobahn-release-artifacts-master-202510180103/*.bfbs
```

**Note:** These artifacts are used during RTD builds via `.github/scripts/rtd-download-artifacts.sh`.
For local testing, use `just docs-integrate-github-release` to copy them into the docs build directory.

**Troubleshooting:**

If downloads fail:
1. Check that the release exists: `https://github.com/crossbario/autobahn-python/releases`
2. Verify the artifact names match the release (especially for nightly vs stable)
3. For older releases (before v25.10.1), these artifacts may not exist - use a newer nightly release

## 7. Documentation Build

Build the documentation locally:

```bash
just docs-integrate-github-release
just docs
```

**Expected:** Build completes successfully (some warnings about missing artifacts OK).

Open docs for visual inspection:

```bash
just docs-view
```

This opens `docs/_build/html/index.html` in your browser.

### 7.1 Docs: Release Notes

**Manual verification:**

1. Open: `http://localhost:8000/index.html` (or the URL from `just docs-view`)
2. Navigate to Release Notes section
3. **Check:**
   - ✅ v25.10.1 is listed
   - ✅ Release date is correct
   - ✅ Major changes are documented
   - ✅ Links work (GitHub issues, PRs)

### 7.2 Docs: Changelog

**Manual verification:**

1. Open: `http://localhost:8000/changelog.html`
2. **Check:**
   - ✅ v25.10.1 entry exists at the top
   - ✅ All changes from `docs/changelog.rst` are rendered correctly
   - ✅ Formatting is correct (bullet points, code blocks)
   - ✅ Issue links work (#1714, #1715, #1716, #1717)

### 7.3 Docs: Wheels Inventory

**Manual verification:**

1. Open: `http://localhost:8000/installation.html` (or wherever wheels are documented)
2. **Check:**
   - ✅ Supported Python versions listed (3.11, 3.12, 3.13, 3.14, PyPy 3.11)
   - ✅ Supported platforms listed (Linux, macOS, Windows)
   - ✅ Installation instructions are clear
   - ✅ NVX acceleration mentioned with `AUTOBAHN_USE_NVX` instructions

### 7.4 Docs: Conformance Reports

**Manual verification:**

1. Open: `http://localhost:8000/websocket/conformance.html`
2. **Check:**
   - ⚠️  **Note:** Reports won't be present in local build (they come from GitHub Release artifacts in RTD)
   - ✅ Page structure exists
   - ✅ Placeholder or message about reports is present
   - ✅ Links to external conformance reports work (if any)

**After RTD publishes v25.10.1:**
- Open: `https://autobahnpython.readthedocs.io/en/v25.10.1/websocket/conformance.html`
- Verify conformance reports load correctly (with-nvx and without-nvx)

### 7.5 Docs: FlatBuffers Schemata

**Manual verification:**

1. Open: `http://localhost:8000/wamp/serialization.html` (or wherever FlatBuffers are documented)
2. **Check:**
   - ⚠️  **Note:** Schema files won't be present in local build (they come from GitHub Release artifacts in RTD)
   - ✅ FlatBuffers serialization is documented
   - ✅ Schema file references are present
   - ✅ Usage examples exist

**After RTD publishes v25.10.1:**
- Open: `https://autobahnpython.readthedocs.io/en/v25.10.1/wamp/serialization.html`
- Verify FlatBuffers schema files are accessible (`.fbs` and `.bfbs` files)

## 8. Release Process

Once all checks pass, Git tag the release:

```bash
git checkout master
git pull origin master
git tag -a v25.10.1 -m "tagged release"
git push origin v25.10.1
```
